from app.services.lip_sync_service import (
    LipSyncService
)


service = LipSyncService()


lip_movements = [
    0.10,
    0.20,
    0.45,
    0.30,
    0.15,
    0.40,
    0.50,
    0.20,
]

audio_levels = [
    0.08,
    0.18,
    0.40,
    0.32,
    0.12,
    0.38,
    0.48,
    0.22,
]


result = service.calculate(
    lip_movements,
    audio_levels
)


print("DTW distance:")
print(result["dtw_distance"])

print("Lip-audio alignment:")
print(result["lip_audio_alignment"])

print("Samples:")
print(result["samples"])
