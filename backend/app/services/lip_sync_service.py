import numpy as np


class LipSyncService:

    def _normalize(self, values):
        if not values:
            return []

        values = np.asarray(
            values,
            dtype=np.float32
        )

        minimum = np.min(values)
        maximum = np.max(values)

        if maximum - minimum < 0.000001:
            return [0.0 for _ in values]

        normalized = (
            values - minimum
        ) / (
            maximum - minimum
        )

        return normalized.tolist()

    def _dtw_distance(
        self,
        sequence_a,
        sequence_b
    ):

        if not sequence_a or not sequence_b:
            return 0.0

        a = np.asarray(
            sequence_a,
            dtype=np.float32
        )

        b = np.asarray(
            sequence_b,
            dtype=np.float32
        )

        rows = len(a)
        columns = len(b)

        dtw = np.full(
            (rows + 1, columns + 1),
            np.inf,
            dtype=np.float32
        )

        dtw[0, 0] = 0.0

        for i in range(1, rows + 1):

            for j in range(1, columns + 1):

                cost = abs(
                    float(a[i - 1])
                    - float(b[j - 1])
                )

                previous = min(
                    dtw[i - 1, j],
                    dtw[i, j - 1],
                    dtw[i - 1, j - 1],
                )

                dtw[i, j] = (
                    cost + previous
                )

        distance = float(
            dtw[rows, columns]
        )

        path_length = (
            rows + columns
        )

        if path_length > 0:
            distance = (
                distance
                / path_length
            )

        return distance

    def calculate(
        self,
        lip_movements,
        audio_levels
    ):

        if (
            not lip_movements
            or not audio_levels
        ):
            return {
                "dtw_distance": 0.0,
                "lip_audio_alignment": 0.0,
                "samples": 0,
            }

        lip = self._normalize(
            lip_movements
        )

        audio = self._normalize(
            audio_levels
        )

        distance = self._dtw_distance(
            lip,
            audio
        )

        alignment = max(
            0.0,
            1.0 - distance
        )

        return {
            "dtw_distance": round(
                distance,
                4
            ),

            "lip_audio_alignment": round(
                alignment,
                4
            ),

            "samples": min(
                len(lip),
                len(audio)
            ),
        }