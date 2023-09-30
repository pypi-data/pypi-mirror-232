import unittest
import lib


class TestLib(unittest.TestCase):
    def test_clean_rut(self):
        self.assertEqual(lib.clean_rut('1.234.567-8'), '12345678')
        self.assertEqual(lib.clean_rut('1.234.5678'), '12345678')
        self.assertEqual(lib.clean_rut('12345678'), '12345678')
        self.assertEqual(lib.clean_rut('123456789'), '123456789')
        self.assertEqual(lib.clean_rut('12345678-9'), '123456789')
        self.assertEqual(lib.clean_rut('12345678-K'), '12345678K')
        self.assertEqual(lib.clean_rut('12345678k'), '12345678K')
        self.assertEqual(lib.clean_rut('K'), 'K')
        self.assertEqual(lib.clean_rut('k'), 'K')
        self.assertEqual(lib.clean_rut('0'), '0')
        self.assertEqual(lib.clean_rut('00'), '0')
        self.assertEqual(lib.clean_rut('000'), '0')
        self.assertEqual(lib.clean_rut('0000'), '0')

    def test_validate_rut(self):
        self.assertFalse(lib.validate_rut('1.234.567-8'))
        self.assertFalse(lib.validate_rut('1.234.5678'))
        self.assertFalse(lib.validate_rut('12345678'))
        self.assertFalse(lib.validate_rut('123456789'))
        self.assertFalse(lib.validate_rut('12345678-9'))
        self.assertFalse(lib.validate_rut('12345678-K'))
        self.assertFalse(lib.validate_rut('12345678k'))
        self.assertFalse(lib.validate_rut('0'))
        self.assertFalse(lib.validate_rut('00'))
        self.assertFalse(lib.validate_rut('000'))
        self.assertFalse(lib.validate_rut('0000'))

    def test_get_last_digit_of_rut(self):
        self.assertEqual(lib.get_last_digit_of_rut(123), '6')
        self.assertEqual(lib.get_last_digit_of_rut(123456789), '2')
        self.assertEqual(lib.get_last_digit_of_rut(12), '4')

    def test_format_rut(self):
        self.assertEqual(lib.format_rut('1.234.567-8'), '1.234.567-8')
        self.assertEqual(lib.format_rut('1.234.5678'), '1.234.567-8')
        self.assertEqual(lib.format_rut('12345678'), '1.234.567-8')
        self.assertEqual(lib.format_rut('123456789',with_dots=False), '12345678-9')
        self.assertEqual(lib.format_rut('12345678-9'), '12.345.678-9')
        self.assertEqual(lib.format_rut('12345678-K'), '12.345.678-K')
        self.assertEqual(lib.format_rut('12345678k'), '12.345.678-K')
        self.assertEqual(lib.format_rut('K'), 'K')
        self.assertEqual(lib.format_rut('k'), 'K')
        self.assertEqual(lib.format_rut('0'), '0')
        self.assertEqual(lib.format_rut('00'), '0')
        self.assertEqual(lib.format_rut('000'), '0')
        self.assertEqual(lib.format_rut('0000'), '0')

    def test_generate_rut(self):

        self.assertEqual(len(lib.generate_rut(length=7, formatted=False)), 7)
        self.assertEqual(len(lib.generate_rut(length=8, formatted=False)), 8)
        self.assertEqual(len(lib.generate_rut(length=9, formatted=False)), 9)
        self.assertEqual(len(lib.generate_rut(length=10, formatted=False)), 10)
        self.assertEqual(len(lib.generate_rut(length=11, formatted=False)), 11)
        self.assertEqual(len(lib.generate_rut(length=12, formatted=False)), 12)
        self.assertEqual(len(lib.generate_rut(length=13, formatted=False)), 13)
        self.assertEqual(len(lib.generate_rut(length=14, formatted=False)), 14)
        self.assertEqual(len(lib.generate_rut(length=15, formatted=False)), 15)
        self.assertEqual(len(lib.generate_rut(length=16, formatted=False)), 16)
        self.assertEqual(len(lib.generate_rut(length=17, formatted=False)), 17)
        self.assertEqual(len(lib.generate_rut(length=18, formatted=False)), 18)
        self.assertEqual(len(lib.generate_rut(length=19, formatted=False)), 19)
        self.assertEqual(len(lib.generate_rut(length=20, formatted=False)), 20)
        self.assertTrue(lib.validate_rut(lib.generate_rut()))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=7, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=8, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=9, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=10, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=11, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=12, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=13, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=14, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=15, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=16, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=17, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=18, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=19, formatted=False)))
        self.assertTrue(lib.validate_rut(
            lib.generate_rut(length=20, formatted=False)))


if __name__ == '__main__':
    unittest.main()
