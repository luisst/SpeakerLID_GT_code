

from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained("pyannote/overlapped-speech-detection",
                                    use_auth_token="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")
output = pipeline("G-C2L1P-Feb16-B-Shelby_q2_03-05_rnd-002.wav")

for speech in output.get_timeline().support():
    # two or more speakers are active between speech.start and speech.end
    print(f'The segments are: {speech}')