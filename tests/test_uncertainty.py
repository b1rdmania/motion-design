import math
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
    check.beat_review(r, 'final', 'sheet')
    f = finding(r, 'beat.review')
    assert f['status'] == 'needs_review' and f['blocking'] and 'Claims' in f['evidence']
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
    check.beat_review(r, 'final', 'sheet')
    assert 'Text appears when planned' in finding(r, 'beat.review')['evidence']


def test_explicit_zero_hold_is_not_replaced_by_beat_duration():
    s = score('Read me'); s['beats'][0]['super']['hold'] = 0
    r = check.Review(s, {})
    check.communication(r, 'final', 'sheet')
    assert finding(r, 'communication.reading_time_plan')['status'] == 'fail'


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
    assert [f['t'] for f in r.findings if f['rule'] == 'communication.reading_time_plan'] == [.2, 1]
    check.beat_review(r, 'final', 'sheet')
    text = [f for f in r.findings if f['rule'] == 'beat.review']
    assert len(text) == 1 and "'First' from 0.20s" in text[0]['evidence'] and "'Second' from 1.00s" in text[0]['evidence']
    samples = frames.sample_times(s, 'final', 2, [])
    fps = s.get('fps', 24)
    starts = [x['frame'] for x in samples if x['kind'] == 'text-start']
    assert starts == [math.ceil(.2 * fps - 1e-6), math.ceil(1 * fps - 1e-6)]


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


def test_event_tolerance_does_not_leak_into_unplanned_cut_check():
    s = score()
    s['beats'][0]['dur'] = 4
    r = check.Review(s, {})
    events = [{'type': 'cut', 't': 1.0}, {'type': 'hit', 't': 3.0, 'tolerance_frames': 100}]
    check.fidelity(r, {'cuts': [{'t': 1.0}, {'t': 2.5}]}, {'has_audio': True, 'onsets': [3.0]}, events, 'final')
    unplanned = [f for f in r.findings if f['rule'] == 'fidelity.unplanned_cut']
    assert [f['t'] for f in unplanned] == [2.5]


def test_continuous_camera_skips_hold_heuristic_once():
    s = score()
    s['camera'] = 'continuous'
    s['beats'][0]['motion'] = {'build': 0, 'hold': 2}
    r = check.Review(s, {})
    check.fidelity(r, {'cuts': [], 'still_runs': []}, {'has_audio': False}, [], 'final')
    holds = [f for f in r.findings if f['rule'] == 'fidelity.hold']
    assert [f['status'] for f in holds] == ['not_applicable']


@pytest.mark.parametrize('start,flagged', [(4.367, True), (4.3667, False), (131 / 30, False)])
def test_frame_alignment_flags_the_documented_off_frame_value(start, flagged):
    s = {'fps': 30, 'beats': [{'id': 'b1', 'start': start, 'dur': 1}]}
    r = check.Review(s, {})
    check.frame_alignment(r)
    assert (finding(r, 'plan.frame_aligned')['status'] == 'needs_review') is flagged


def test_deliver_reports_a_missing_render_instead_of_crashing(tmp_path):
    crit = tmp_path / 'critique.json'
    crit.write_text(json.dumps({'stage': 'final', 'findings': []}))
    lines, ok = deliver.section(tmp_path / 'gone.mp4', crit, tmp_path)
    assert not ok and any('not found' in line for line in lines)


def test_permitted_wording_compares_only_the_cue_that_states_the_claim():
    s = score()
    s['beats'][0].pop('super')
    s['beats'][0]['proves'] = 'c1'
    # The claim is printed on a sleeve in the picture; the only super is the audience line.
    s['beats'][0]['text_cues'] = [
        {'text': 'For people who read the back of the sleeve', 'start': 0, 'hold': 2, 'claim': None}]
    ledger = {'claims': [{'id': 'c1', 'type': 'fact', 'source': 'db', 'evidence': 'row 1',
                          'permitted_wording': 'Remixed by Monolake'}]}
    r = check.Review(s, {})
    check.evidence(r, ledger, 'final')
    assert not [f for f in r.findings if f['rule'] == 'evidence.permitted_wording']
    # A cue that does state the claim is still held to the permitted wording.
    s['beats'][0]['text_cues'].append({'text': 'Remix by Monolake', 'start': 0, 'hold': 2, 'claim': 'c1'})
    r = check.Review(s, {})
    check.evidence(r, ledger, 'final')
    assert [f for f in r.findings if f['rule'] == 'evidence.permitted_wording']


def test_missing_music_file_is_caught_at_plan_time(tmp_path):
    plan = tmp_path / 'plan'
    plan.mkdir()
    s = score()
    s['music'] = {'track': 'audio/music.wav'}
    r = check.Review(s, {})
    check.music_track(r, plan)
    assert finding(r, 'plan.music_track')['status'] == 'fail'
    (tmp_path / 'audio').mkdir()
    (tmp_path / 'audio' / 'music.wav').write_bytes(b'')
    r = check.Review(s, {})
    check.music_track(r, plan)
    assert finding(r, 'plan.music_track')['status'] == 'pass'
    s['music'] = {'track': 'sine 440 Hz test tone'}
    r = check.Review(s, {})
    check.music_track(r, plan)
    assert not [f for f in r.findings if f['rule'] == 'plan.music_track']
