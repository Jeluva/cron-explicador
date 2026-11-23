import sys, os, unittest
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cronx


class T(unittest.TestCase):
    def test_proximas_cada_15(self):
        r = cronx.proximas("*/15 * * * *", datetime(2026, 1, 1, 10, 0), 3)
        self.assertEqual([d.minute for d in r], [15, 30, 45])

    def test_lunes_a_viernes(self):
        r = cronx.proximas("0 9 * * mon-fri", datetime(2026, 1, 2, 9, 0), 3)  # viernes
        self.assertEqual([d.day for d in r], [5, 6, 7])

    def test_alias(self):
        self.assertEqual(cronx.proximas("@monthly", datetime(2026, 1, 15), 1)[0].month, 2)

    def test_invalidos(self):
        for e in ("60 * * * *", "* * *", "5-1 * * * *", "*/0 * * * *", "a * * * *"):
            with self.assertRaises(cronx.CronError):
                cronx.parsear(e)

    def test_explicar(self):
        self.assertIn("dia de la semana: lunes, martes", cronx.explicar("0 0 * * 1-2")[4])


if __name__ == "__main__":
    unittest.main()
