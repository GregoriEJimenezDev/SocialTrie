import ast
import io
import pathlib
import unittest
from contextlib import redirect_stdout
from unittest import mock

import main as app_main
from socialtrie.exceptions import (DeletedPostError, DomainError, DuplicateBannedWordError,
                                   EntityNotFoundError, InactiveUserError, ValidationError)
from socialtrie.factories import EntityFactory
from socialtrie.models import BannedWordStatus, CommentStatus, PostStatus, UserStatus
from socialtrie.moderation import DetectionHistory, Moderator
from socialtrie.repositories import Repository
from socialtrie.services import (BannedWordService, CommentService, MetricsService, PostService,
                                 SystemStatusService, UserService)
from socialtrie.trie import Trie

ROOT = pathlib.Path(__file__).resolve().parent.parent


def make():
    users, posts, comments, words = (Repository() for _ in range(4))
    trie, factory, history = Trie(), EntityFactory(), DetectionHistory()
    us = UserService(users, posts, factory)
    ps = PostService(posts, comments, us, factory)
    cs = CommentService(comments, ps, us, factory, Moderator(trie), history)
    ws = BannedWordService(words, trie, factory)
    ms = MetricsService(users, posts, comments, history)
    st = SystemStatusService(users, posts, comments, words, trie)
    return us, ps, cs, ws, ms, st, trie


class TrieTests(unittest.TestCase):
    def test_trie(self):
        t = Trie()
        self.assertTrue(t.is_empty())
        t.insert("mal")
        self.assertTrue(t.search("mal"))
        self.assertFalse(t.search("ma"))
        self.assertFalse(t.search("malo"))
        self.assertTrue(t.starts_with("ma"))
        self.assertTrue(t.remove("mal"))
        self.assertTrue(t.is_empty())


class ModerationTests(unittest.TestCase):
    def setUp(self):
        self.us, self.ps, self.cs, self.ws, self.ms, self.st, self.trie = make()
        self.ws.add("Mal")
        self.m = Moderator(self.trie)

    def test_cases(self):
        cases = {"Mal día": "***** día", "malo malestar maldito": "malo malestar maldito",
                 "(MAL),": "(*****),", "MAL?!": "*****?!", "¡Mal!": "¡Mal!", "'mal'": "'*****'", "’mal’": "’*****’",
                 "mal mal MAL": "***** ***** *****", "hola mundo": "hola mundo"}
        for raw, expected in cases.items():
            self.assertEqual(self.m.moderate(raw).moderated_text, expected, raw)
        self.assertEqual(self.m.moderate("mal mal MAL").censorship_count, 3)

    def test_empty_trie(self):
        self.assertEqual(Moderator(Trie()).moderate("mal").moderated_text, "mal")

    def test_only_banned(self):
        self.assertEqual(self.m.moderate("mal mal").moderated_text, "***** *****")


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.us, self.ps, self.cs, self.ws, self.ms, self.st, self.trie = make()
        self.ana = self.us.create("ana")
        self.bob = self.us.create("bob")

    def test_users(self):
        self.assertEqual(self.us.create("09").name, "09")
        self.assertEqual(self.us.create("juan2").name, "juan2")
        with self.assertRaises(ValidationError): self.us.create("ANA")
        with self.assertRaises(ValidationError): self.us.create("  ")
        with self.assertRaises(EntityNotFoundError): self.us.rename(99, "x")
        self.us.rename(1, "ana"); self.us.rename(1, "ana2"); self.us.create("ana")  # nombre liberado

    def test_inactive_user(self):
        self.us.set_active(1, False)
        with self.assertRaises(InactiveUserError): self.ps.create(1, "t", "c")
        post = self.ps.create(2, "t", "c")
        with self.assertRaises(InactiveUserError): self.cs.add(post.id, 1, "hola")

    def test_cannot_inactivate_user_with_active_posts(self):
        p = self.ps.create(1, "t", "c")
        with self.assertRaises(ValidationError): self.us.set_active(1, False)
        self.assertEqual(self.us.get(1).status, UserStatus.ACTIVE)
        self.ps.delete(p.id)
        self.us.set_active(1, False)  # sin posts activos ya se permite
        self.assertEqual(self.us.get(1).status, UserStatus.INACTIVE)

    def test_post_rules(self):
        p = self.ps.create(1, "t", "c")
        c = self.cs.add(p.id, 2, "hola")
        with self.assertRaises(ValidationError): self.ps.delete(p.id)
        self.cs.delete(c.id)
        self.ps.delete(p.id)
        self.assertEqual(p.status, PostStatus.DELETED)
        with self.assertRaises(ValidationError): self.ps.delete(p.id)
        with self.assertRaises(DeletedPostError): self.cs.add(p.id, 2, "x")
        with self.assertRaises(DeletedPostError): self.cs.edit(c.id, "x")
        self.assertEqual(len(self.cs.list_for_post(p.id)), 1)
        with self.assertRaises(ValidationError): self.ps.create(1, "", "c")

    def test_ids_not_reused(self):
        p1 = self.ps.create(1, "t", "c"); self.ps.delete(p1.id)
        self.assertEqual(self.ps.create(1, "t", "c").id, 2)

    def test_words(self):
        w = self.ws.add("MAL ")
        with self.assertRaises(DuplicateBannedWordError): self.ws.add("mal")
        self.ws.set_active(w.id, False)
        self.assertTrue(self.trie.is_empty())
        self.ws.add("mal")  # permitido: la anterior está inactiva
        with self.assertRaises(DuplicateBannedWordError): self.ws.set_active(w.id, True)
        with self.assertRaises(EntityNotFoundError): self.ws.edit(99, "x")
        w2 = self.ws.add("feo"); self.ws.edit(w2.id, "Feote")
        self.assertTrue(self.trie.search("feote")); self.assertFalse(self.trie.search("feo"))

    def test_deactivate_reactivate(self):
        w = self.ws.add("mal"); p = self.ps.create(1, "t", "c")
        self.ws.set_active(w.id, False)
        self.assertEqual(self.cs.add(p.id, 1, "mal").censorship_count, 0)
        self.ws.set_active(w.id, True)
        self.assertEqual(self.cs.add(p.id, 1, "mal").censorship_count, 1)

    def test_edit_comment_status(self):
        self.ws.add("mal"); p = self.ps.create(1, "t", "c")
        c = self.cs.add(p.id, 1, "hola")
        self.assertEqual(c.status, CommentStatus.PUBLISHED)
        self.cs.edit(c.id, "mal")
        self.assertEqual((c.status, c.moderated_text, p.censorship_count), (CommentStatus.EDITED, "*****", 1))
        with self.assertRaises(ValidationError): self.cs.add(p.id, 1, "   ")


class MetricsTests(unittest.TestCase):
    def test_empty(self):
        m = make()[4].generate()
        self.assertEqual((m.total_comments, m.average_censorship, m.top_words), (0, 0.0, []))

    def test_ties_and_deleted(self):
        us, ps, cs, ws, ms, st, trie = make()
        us.create("zoe"); us.create("ana")
        ws.add("beta"); ws.add("alfa")
        pz = ps.create(1, "Zeta", "c"); pa = ps.create(2, "Alfa", "c")
        cs.add(pz.id, 1, "beta"); cs.add(pa.id, 2, "alfa")
        gone = cs.add(pa.id, 2, "alfa alfa alfa"); cs.delete(gone.id)
        m = ms.generate()
        self.assertEqual(m.user_ranking[0], ("ana", 1))        # desempate alfabético
        self.assertEqual(m.post_ranking[0][0], "Alfa")
        self.assertEqual(m.top_words[0][0], "alfa")            # histórico incluye lo eliminado: 4 vs 1
        self.assertEqual(m.active_comments, 2); self.assertEqual(m.deleted_comments, 1)
        self.assertAlmostEqual(m.average_censorship, 1.0)      # solo activos
        self.assertEqual(m.total_censored, sum(n for _, n in m.top_words))

    def test_tie_words(self):
        us, ps, cs, ws, ms, st, trie = make()
        us.create("a"); ws.add("beta"); ws.add("alfa"); p = ps.create(1, "t", "c")
        cs.add(p.id, 1, "beta alfa")
        self.assertEqual([w for w, _ in ms.generate().top_words], ["alfa", "beta"])

    def test_status(self):
        us, ps, cs, ws, ms, st, trie = make()
        self.assertTrue(st.snapshot().trie_empty)
        ws.add("x"); us.create("a")
        s = st.snapshot()
        self.assertEqual((s.users["Activo"], s.words["Activa"], s.trie_empty), (1, 1, False))


def run_ui(lines):
    out = io.StringIO()
    with mock.patch("builtins.input", side_effect=lines), redirect_stdout(out):
        try:
            app_main.main()
        except StopIteration:
            pass
    return " ".join(out.getvalue().split())


class UITests(unittest.TestCase):
    def test_invalid_ids_no_python_errors(self):
        out = run_ui(["2", "1", "ds", "1", "", "1", "-1", "1", "0", "6", "9", "s"])
        self.assertNotIn("invalid literal", out)
        self.assertIn("Debe ingresar un número entero positivo", out)
        self.assertIn("RESUMEN FINAL", out)

    def test_search_post_by_id(self):
        out = run_ui(["1", "1", "09", "7", "2", "1", "01", "Titulo", "Cont", "6",
                      "3", "01", "3", "99", "9", "n", "9", "s"])
        self.assertIn("Autor: 09", out); self.assertIn("Título: Titulo", out)
        self.assertIn("Post inexistente", out)
        self.assertNotIn("Post(id=", out)

    def test_full_flow_and_exit(self):
        out = run_ui(["6", "1", "mal", "6", "1", "1", "ana", "7", "2", "1", "1", "T", "C", "6",
                      "4", "1", "1", "Mal dia, mal!", "5", "1", "", "7", "8", "9", "s"])
        self.assertIn("***** dia, *****!", out)
        self.assertIn("1. mal (2)", out)
        self.assertIn("Trie vacío: No", out)
        self.assertIn("Total de palabras censuradas: 2", out)

    def test_eof_closes_cleanly(self):
        out = run_ui(["1", "1", "x", EOFError()])
        self.assertIn("Cerrando SocialTrie", out); self.assertIn("RESUMEN FINAL", out)


class BigOTests(unittest.TestCase):
    def test_every_function_has_complexity_comment(self):
        missing = []
        for path in list(ROOT.glob("main.py")) + list(ROOT.glob("socialtrie/**/*.py")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for node in ast.walk(ast.parse("\n".join(lines))):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                    window = lines[max(0, start - 3):node.lineno]
                    if not any("Complejidad" in l for l in window):
                        missing.append(f"{path.name}:{node.name}")
        self.assertEqual(missing, [])

    def test_moderation_does_not_use_forbidden_structures(self):
        src = (ROOT / "socialtrie/moderation/moderator.py").read_text(encoding="utf-8")
        self.assertIn("self.trie.search(", src)
        for bad in (".replace(", "banned_words", "re.sub", "re.compile"):
            self.assertNotIn(bad, src)


if __name__ == "__main__":
    unittest.main()
