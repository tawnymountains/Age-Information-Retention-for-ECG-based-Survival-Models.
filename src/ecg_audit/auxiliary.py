"""Small generic PyTorch wrapper; the paper's encoder/checkpoints are not shipped."""
import torch
from torch import nn
import math


class AgeAuxiliary(nn.Module):
    """Attach age prediction to any encoder returning [batch, representation_dim]."""
    def __init__(self, encoder, representation_dim):
        super().__init__()
        self.encoder = encoder
        self.age_head = nn.Linear(representation_dim, 1)

    def forward(self, waveform):
        representation = self.encoder(waveform)
        return representation, self.age_head(representation).squeeze(-1)

    def encoder_for_inference(self):
        # Removing the auxiliary head does not make chronological age an input.
        return self.encoder


def age_augmented_loss(original_loss, predicted_age, target_age, *, age_weight, huber_delta):
    """Keep the caller's SL/SSL objective; age normalization and weight are explicit."""
    if not math.isfinite(age_weight) or not math.isfinite(huber_delta) or age_weight < 0 or huber_delta <= 0:
        raise ValueError("Nonnegative age weight and positive Huber delta required")
    age_loss = torch.nn.functional.huber_loss(predicted_age, target_age, delta=huber_delta)
    return original_loss + age_weight * age_loss
