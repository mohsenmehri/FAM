"""تست برای بررسی فایل‌های بازنویسی‌شده توسط ایجنت ۱ (CCNA/ADV/CCNP).

این تست مستقیماً فایل‌های agent1_rewrites/*.json را بررسی می‌کند،
نه داده اصلی academy-data.json (که تغییر نکرده است).
"""

import json
import glob
import os
import unittest

REWRITE_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'agent1_rewrites'
)

# Lesson IDs in Agent 1 scope: ccna_* except ccna_01/02, adv_*, ccnp_*
AGENT1_SCOPE = [
    'adv_01', 'adv_02', 'adv_03', 'adv_04', 'adv_bfd', 'adv_bgp', 'adv_ec',
    'adv_eigrp', 'adv_mcast', 'adv_pvl', 'adv_qos', 'adv_redist',
    'ccna_02_vlan', 'ccna_03', 'ccna_04', 'ccna_05', 'ccna_06',
    'ccna_acl', 'ccna_dhcp', 'ccna_nat', 'ccna_qos_ssh', 'ccna_v1',
    'ccna_v6', 'ccna_wl',
    'ccnp_01', 'ccnp_02', 'ccnp_enauto', 'ccnp_enc_arch', 'ccnp_enc_auto',
    'ccnp_enc_inf', 'ccnp_enc_sec', 'ccnp_encc', 'ccnp_enna',
    'ccnp_ensdwi', 'ccnp_ensld',
]


class TestAgent1Rewrites(unittest.TestCase):
    """تست فایل‌های بازنویسی‌شده ایجنت ۱"""

    def setUp(self):
        self.rewrites = {}
        for lid in AGENT1_SCOPE:
            path = os.path.join(REWRITE_DIR, f'{lid}.json')
            if os.path.exists(path):
                with open(path, encoding='utf-8') as f:
                    self.rewrites[lid] = json.load(f)
            else:
                self.rewrites[lid] = None

    def test_all_35_rewrite_files_exist(self):
        """همه ۳۵ فایل بازنویسی وجود داشته باشند."""
        missing = [lid for lid in AGENT1_SCOPE if self.rewrites[lid] is None]
        self.assertEqual(len(missing), 0, f"فایل‌های بازنویسی غایب: {missing}")

    def test_each_rewrite_has_lab_type(self):
        """هر فایل بازنویسی باید labType در lab داشته باشد."""
        for lid in AGENT1_SCOPE:
            lesson = self.rewrites[lid]
            self.assertIsNotNone(lesson, f"{lid}: فایل غایب")
            lab_type = lesson.get('lab', {}).get('labType')
            self.assertIsNotNone(lab_type, f"{lid}: labType غایب است")
            self.assertIn(lab_type, ['Mock', 'Reference', 'Executed'],
                         f"{lid}: labType نامعتبر: {lab_type}")

    def test_each_rewrite_keeps_original_id(self):
        """شناسه lesson در فایل بازنویسی همان نام فایل باشد."""
        for lid in AGENT1_SCOPE:
            lesson = self.rewrites[lid]
            self.assertIsNotNone(lesson, f"{lid}: فایل غایب")
            self.assertEqual(lesson.get('id'), lid,
                           f"{lid}: id mismatch: {lesson.get('id')}")

    def test_each_rewrite_has_complete_components(self):
        """هر درس باید analogy، summary، quiz(3+)، exercises(3+)، lab داشته باشد."""
        for lid in AGENT1_SCOPE:
            lesson = self.rewrites[lid]
            self.assertIsNotNone(lesson, f"{lid}: فایل غایب")
            self.assertTrue(lesson.get('analogy'), f"{lid}: analogy غایب")
            self.assertTrue(lesson.get('summary'), f"{lid}: summary غایب")
            quiz = lesson.get('quiz', [])
            self.assertGreaterEqual(len(quiz), 3, f"{lid}: quiz[{len(quiz)}] < 3")
            exercises = lesson.get('exercises', [])
            self.assertGreaterEqual(len(exercises), 3, f"{lid}: exercises[{len(exercises)}] < 3")
            lab = lesson.get('lab', {})
            self.assertTrue(lab.get('steps'), f"{lid}: lab steps غایب")
            self.assertTrue(lab.get('verifyCmds'), f"{lid}: lab verifyCmds غایب")

    def test_quiz_answers_in_range(self):
        """پاسخ کوییز باید در بازه معتبر باشد و توضیح داشته باشد."""
        for lid in AGENT1_SCOPE:
            lesson = self.rewrites[lid]
            self.assertIsNotNone(lesson, f"{lid}: فایل غایب")
            for i, q in enumerate(lesson.get('quiz', [])):
                opts = q.get('opts', [])
                ans = q.get('ans', -1)
                self.assertGreaterEqual(ans, 0, f"{lid} Q{i}: ans منفی")
                self.assertLess(ans, len(opts), f"{lid} Q{i}: ans={ans} در 범위 opts[{len(opts)}] نیست")
                self.assertTrue(q.get('exp'), f"{lid} Q{i}: exp (توضیح پاسخ) غایب")

    def test_exercises_have_solutions(self):
        """همه تمرین‌ها باید حل tenido داشته باشند."""
        for lid in AGENT1_SCOPE:
            lesson = self.rewrites[lid]
            self.assertIsNotNone(lesson, f"{lid}: فایل غایب")
            for i, ex in enumerate(lesson.get('exercises', [])):
                self.assertTrue(ex.get('solution'), f"{lid} Ex{i}: solution غایب")
                self.assertTrue(ex.get('task'), f"{lid} Ex{i}: task غایب")

    def test_ccna_02_vlan_keeps_4_quiz_questions(self):
        """ccna_02_vlan باید ۴ سوال کوییز داشته باشد (حذف سوال برای پاس错了 است)."""
        lesson = self.rewrites.get('ccna_02_vlan')
        self.assertIsNotNone(lesson, "ccna_02_vlan: فایل غایب")
        self.assertEqual(len(lesson.get('quiz', [])), 4,
                        f"ccna_02_vlan quiz count: {len(lesson.get('quiz', []))} (باید ۴ باشد)")

    def test_no_placeholder_content_field(self):
        "حذف فیلد قالبی content (commit 528e2a0 رد شده) باید حفظ شود."
        for lid in AGENT1_SCOPE:
            lesson = self.rewrites[lid]
            self.assertIsNotNone(lesson, f"{lid}: فایل غایب")
            self.assertNotIn('content', lesson,
                           f"{lid}: فیلد قالبی 'content' هنوز موجود است!")


if __name__ == '__main__':
    unittest.main()


class TestAgent1LabTypeAccuracy(unittest.TestCase):
    """تست دقت labType بر اساس تحلیل صحت شبیه‌ساز"""

    def setUp(self):
        self.rewrites = {}
        for lid in AGENT1_SCOPE:
            path = os.path.join(REWRITE_DIR, f'{lid}.json')
            if os.path.exists(path):
                with open(path, encoding='utf-8') as f:
                    self.rewrites[lid] = json.load(f)

    def test_labtype_not_executed_without_evidence(self):
        """هیچ lesson نباید 'Executed' باشد چون اجرا_real_ تأیید نشده."""
        for lid in AGENT1_SCOPE:
            lesson = self.rewrites[lid]
            self.assertIsNotNone(lesson, f"{lid}: فایل غایب")
            lab_type = lesson.get('lab', {}).get('labType')
            self.assertNotEqual(lab_type, 'Executed',
                              f"{lid}: labType='Executed' بدون شوأد اجرا_real_")

    def test_labtype_consistent_with_sim_honesty(self):
        """labType باید با صحت شبیه‌ساز در خطوات laboratoire همسو باشد."""
        path = os.path.join(
            os.path.dirname(__file__), '..', '..',
            '01-خام-پروژه', 'server', 'www', 'academy-assets', 'academy-data.json'
        )
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        lessons = data['lessons']

        for lid in AGENT1_SCOPE:
            lesson = lessons[lid]
            rewrite = self.rewrites[lid]
            lab_type = rewrite.get('lab', {}).get('labType')

            all_step_text = ' '.join(lesson.get('lab', {}).get('steps', [])).lower()
            sim_honest = ('شبیه‌ساز' in all_step_text and
                         ('اجرا نمی‌کند' in all_step_text or 'پشتیبانی نمی‌کند' in all_step_text))

            if sim_honest:
                self.assertEqual(lab_type, 'Reference',
                               f"{lid}: sim صادقانه است اما labType={lab_type}")
            elif 'mock' in all_step_text:
                self.assertEqual(lab_type, 'Mock',
                               f"{lid}: mock است اما labType={lab_type}")

    def test_ccna_v6_verifycmds_count(self):
        """ccna_v6 باید ۳ verifyCmds داشته باشد (بسته به محتوای laboratoire)."""
        lesson = self.rewrites.get('ccna_v6')
        self.assertIsNotNone(lesson, "ccna_v6: فایل غایب")
        verify_cmds = lesson.get('lab', {}).get('verifyCmds', [])
        self.assertEqual(len(verify_cmds), 3,
                        f"ccna_v6 verifyCmds count: {len(verify_cmds)} (باید ۳ باشد)")


if __name__ == '__main__':
    unittest.main()
