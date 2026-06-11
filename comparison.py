import librosa
import numpy as np

def compare_audio(file1, file2):
    try:
        print("FILE1 =", file1)
        print("FILE2 =", file2)

        print("Loading:", file1)
        y1, sr1 = librosa.load(file1, sr=16000, mono=True)

        print("Loading:", file2)
        y2, sr2 = librosa.load(file2, sr=16000, mono=True)

        mfcc1 = librosa.feature.mfcc(y=y1, sr=sr1)
        mfcc2 = librosa.feature.mfcc(y=y2, sr=sr2)

        diff = np.mean(
            np.abs(
                np.mean(mfcc1, axis=1)
                - np.mean(mfcc2, axis=1)
            )
        )

        print("DIFF =", diff)

        return float(diff)

    except Exception as e:
        print("Voice comparison error:", repr(e))
        return 999