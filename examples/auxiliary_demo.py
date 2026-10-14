"""Optional PyTorch illustration, not the study's encoder or training recipe."""
import torch
from torch import nn
from ecg_audit.auxiliary import AgeAuxiliary, age_augmented_loss


def main():
    torch.manual_seed(2026)  # Arbitrary synthetic-demo seed only.
    encoder = nn.Sequential(nn.Flatten(), nn.Linear(12 * 64, 32), nn.ReLU())
    model = AgeAuxiliary(encoder, representation_dim=32)
    synthetic_waveforms = torch.randn(8, 12, 64)
    representation, predicted_age = model(synthetic_waveforms)
    synthetic_age = torch.randn(8)  # Illustrative standardized target, not real ages.
    toy_original_objective = representation.square().mean()
    loss = age_augmented_loss(toy_original_objective, predicted_age, synthetic_age,
                              age_weight=.2, huber_delta=1.)
    loss.backward()
    assert model.age_head.weight.grad.abs().sum() > 0
    assert encoder[1].weight.grad.abs().sum() > 0
    assert model.encoder_for_inference()(synthetic_waveforms).shape == (8, 32)
    print("PASS: synthetic auxiliary gradients and ECG-only encoder interface; no paper training reproduced.")


if __name__ == "__main__":
    main()
