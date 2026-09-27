"""Regression cases where proxies previously claimed certainty about a film."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audio_check
import check
import deliver
import frames
import motion_strip
from resolve import resolve
from _common import effective_status, plan_version, review_summary, sha256_file


def score(text=''):
    return {'fps': 24, 'duration': 2, 'delivery': {}, 'beats': [
        {'id': 'b1', 'start': 0, 'dur': 2, 'super': {'text': text, 'hold': 2}}]}


def finding(r, rule):
    return next(f for f in r.findings if f['rule'] == rule)


def test_small_area_cut_is_uncertain_not_failed():
    picture = np.zeros((48, 90, 160, 3), dtype=np.float32)
    picture[24:, 35:55, 70:90, :] = 1
    strip = motion_strip.analyse(picture, 24)
    r = check.Review(score(), {})
    check.fidelity(r, strip, {}, [{'type': 'cut', 't': 1}], 'final')
    assert finding(r, 'fidelity.cut')['status'] == 'needs_review'


def test_opposite_polarity_stereo_is_not_silence():
    t = np.arange(48000) / 48000
    tone = .1 * np.sin(2 * np.pi * 440 * t)
    result = audio_check.analyse(np.stack([tone, -tone], axis=1), -50, .25)
    assert result['silences'] == []


@pytest.mark.parametrize('start,end,expected', [(1, 2, 'pass'), (1, 1.3, 'needs_review'),
                                               (1, 2.4, 'needs_review'), (1.3, 2, 'needs_review')])
def test_silence_checks_both_boundaries(start, end, expected):
    r = check.Review(score(), {})
    audio = {'has_audio': True, 'silences': [{'start': start, 'end': end, 'dur': end-start}]}
    check.fidelity(r, {'cuts': []}, audio, [{'type': 'silence', 't': 1, 'dur': 1}], 'final')
    assert finding(r, 'fidelity.silence')['status'] == expected


def silent_audio():
    return {'has_audio': True, 'clipped_samples': 0, 'integrated_lufs': None,
            'true_peak_dbtp': None, 'max_abs_sample': 0, 'duration': 2,
            'silences': [{'start': 0, 'end': 2, 'dur': 2}]}


@pytest.mark.parametrize('planned,expected', [(True, 'fail'), (False, 'not_applicable')])
def test_silence_requires_explicit_intent(planned, expected):
    r = check.Review(score(), {})
    check.sound(r, silent_audio(), {'audio': planned}, [], 'final')
    assert finding(r, 'sound.loudness')['status'] == expected


def test_measurement_failure_is_not_intended_silence():
    r = check.Review(score(), {})
    a = silent_audio(); a['measurement_error'] = 'analysis failed'
    check.sound(r, a, {'audio': True}, [], 'final')
    assert finding(r, 'sound.loudness')['status'] == 'needs_review'
    assert finding(r, 'sound.measurement')['status'] == 'needs_review'


def test_nonnumeric_claim_requires_coverage_review():
    r = check.Review(score('Guaranteed approval'), {})
    check.evidence(r, {'claims': []})
    assert finding(r, 'evidence.coverage')['status'] == 'needs_review'
    assert not any(f['status'] == 'not_applicable' for f in r.findings)


def test_version_number_is_not_automatically_unsupported_claim():
    r = check.Review(score('Version 2'), {})
    check.evidence(r, {'claims': []})
    assert finding(r, 'evidence.number_anchored')['status'] == 'needs_review'


def test_populated_source_is_not_proof():
    r = check.Review(score('Guaranteed approval'), {})
    check.evidence(r, {'claims': [{'id': 'a', 'type': 'fact', 'source': 'example', 'evidence': 'some text'}]})
    assert finding(r, 'evidence.source_support')['status'] == 'needs_review'


def test_reading_speed_blocks_only_explicit_plan_limit():
    s = score('a' * 60); s['delivery']['max_text_cps'] = 25
    r = check.Review(s, {})
    check.communication(r, 'final', 'sheet')
    f = finding(r, 'communication.reading_time_plan')
    assert f['status'] == 'fail' and f['blocking'] and f['method'] == 'plan'
    assert finding(r, 'communication.rendered_text')['status'] == 'needs_review'


def test_explicit_zero_hold_is_not_replaced_by_beat_duration():
    s = score('Read me'); s['beats'][0]['super']['hold'] = 0
    r = check.Review(s, {})
    check.communication(r, 'final', 'sheet')
    assert finding(r, 'communication.reading_time_plan')['status'] == 'needs_review'


def test_legacy_and_structured_match_cuts_are_cut_events():
    for tr in ['match:circle', {'type': 'cut', 'relationship': 'circle'}]:
        s = score(); s['beats'].append({'id': 'b2', 'start': 1, 'dur': 1, 'transition_in': tr})
        assert check.expected_events(s)[0]['type'] == 'cut'
        r = check.Review(s, {}); check.judged(r, 'final', 'sheet', 'strip')
        assert finding(r, 'judged.transition')['status'] == 'needs_review'


def test_multiple_text_cues_are_timed_and_sampled_independently():
    s = score(); s['beats'][0]['text_cues'] = [
        {'text': 'First', 'start': .2, 'hold': .5}, {'text': 'Second', 'start': 1, 'hold': .8}]
    r = check.Review(s, {}); check.communication(r, 'final', 'sheet')
    assert [f['t'] for f in r.findings if f['rule'] == 'communication.rendered_text'] == [.2, 1]
    samples = frames.sample_times(s, 'final', 2, [])
    assert [.2, 1] == [x['t'] for x in samples if x['kind'] == 'text-start']


def test_resolution_preserves_measurement_and_refreshes_summary():
    original = {'id': 'f0001', 'rule': 'judged.frame', 'status': 'needs_review',
                'blocking': True, 'evidence': 'original observation'}
    crit = {'findings': [original]}
    resolve(crit, 'f0001', 'pass', 'inspected at phone width', 'frame inspection')
    assert original['status'] == 'needs_review' and original['evidence'] == 'original observation'
    assert effective_status(original) == 'pass'
    assert crit['verdict'] == 'clear' and crit['counts']['needs_review'] == 0
    assert not crit['blocking_open']


def test_resolution_cannot_erase_measured_failure():
    crit = {'findings': [{'id': 'f1', 'status': 'fail', 'blocking': True}]}
    with pytest.raises(ValueError):
        resolve(crit, 'f1', 'pass', 'looks okay', 'inspection')


def test_empty_resolution_does_not_pass():
    f = {'status': 'needs_review', 'blocking': True, 'resolution': {'status': 'pass'}}
    assert effective_status(f) == 'needs_review'
    assert review_summary([f])['verdict'] == 'open'


def test_delivery_does_not_invent_completed_review_or_trust_cached_verdict(tmp_path):
    plan = tmp_path / 'plan'; plan.mkdir()
    (plan / 'score.json').write_text('{}')
    video = tmp_path / 'v.mp4'; video.write_bytes(b'file bound to review')
    crit = {'stage': 'final', 'render_sha256': sha256_file(video), 'plan_version': plan_version(plan),
            'round': 1, 'verdict': 'clear', 'blocking_open': 0, 'findings': [
                {'id': 'f1', 'rule': 'communication.speech', 'status': 'needs_review', 'blocking': True,
                 'beat': None, 't': 0, 'evidence': 'not listened'}]}
    path = tmp_path / 'crit.json'; path.write_text(json.dumps(crit))
    lines, ok = deliver.section(video, path, plan)
    text = '\n'.join(lines)
    assert not ok and 'Recorded reviewer decisions:** none' in text
    assert 'Judged by inspecting frames' not in text


def test_quiet_mix_without_explicit_target_is_advice():
    a = silent_audio(); a.update(integrated_lufs=-20, true_peak_dbtp=-5, max_abs_sample=.5, silences=[])
    r = check.Review(score(), {}); check.sound(r, a, {'audio': True}, [], 'final')
    assert not finding(r, 'sound.loudness')['blocking']
    assert finding(r, 'sound.loudness')['status'] == 'needs_review'
