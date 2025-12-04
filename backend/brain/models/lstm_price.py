import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, List, Dict

class TimeSeriesTransformer(nn.Module):
    """
    Transformer-based model for Probabilistic Time-Series Forecasting.
    Replaces the legacy LSTM architecture.
    
    Features:
    - Multi-head Self-Attention for capturing long-range dependencies.
    - Quantile output for probabilistic forecasting (e.g., P10, P50, P90).
    - Handling of multiple time-series inputs.
    """
    
    def __init__(
        self, 
        input_dim: int, 
        d_model: int = 64, 
        nhead: int = 4, 
        num_layers: int = 2, 
        dropout: float = 0.1,
        quantiles: List[float] = [0.1, 0.5, 0.9]
    ):
        """
        Args:
            input_dim (int): Number of input features per time step.
            d_model (int): The number of expected features in the encoder/decoder inputs.
            nhead (int): The number of heads in the multiheadattention models.
            num_layers (int): The number of sub-encoder-layers in the encoder.
            dropout (float): The dropout value.
            quantiles (List[float]): Quantiles to predict for probabilistic forecasting.
        """
        super(TimeSeriesTransformer, self).__init__()
        self.quantiles = quantiles
        self.num_quantiles = len(quantiles)
        
        # Input embedding layer to project features to d_model size
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        # Transformer Encoder
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=d_model*4, dropout=dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        
        # Output heads for each quantile
        # We predict the next step(s). For simplicity, this model predicts the next step's quantiles.
        self.output_layer = nn.Linear(d_model, self.num_quantiles)
        
    def forward(self, src: torch.Tensor, src_mask: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            src (torch.Tensor): Input sequence of shape (batch_size, seq_len, input_dim).
            src_mask (torch.Tensor): Optional mask for the sequence.

        Returns:
            torch.Tensor: Predicted quantiles of shape (batch_size, num_quantiles).
        """
        # Embed and add positional encoding
        x = self.embedding(src) # (batch, seq, d_model)
        x = self.pos_encoder(x)
        
        # Pass through Transformer
        # Output shape: (batch, seq, d_model)
        output = self.transformer_encoder(x, src_mask)
        
        # We take the last time step's embedding to predict the future
        # Shape: (batch, d_model)
        last_step_output = output[:, -1, :]
        
        # Project to quantiles
        # Shape: (batch, num_quantiles)
        prediction = self.output_layer(last_step_output)
        
        return prediction

class PositionalEncoding(nn.Module):
    """Injects some information about the relative or absolute position of the tokens in the sequence."""

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor, shape [batch_size, seq_len, embedding_dim]
        """
        x = x + self.pe[:x.size(1)].transpose(0, 1).transpose(0, 1) # Adjust dimensions to match batch_first=True
        return self.dropout(x)

def quantile_loss(preds: torch.Tensor, target: torch.Tensor, quantiles: List[float]) -> torch.Tensor:
    """
    Calculate the Quantile Loss.
    
    Args:
        preds: Predictions of shape (batch, num_quantiles)
        target: Actual values of shape (batch, 1)
        quantiles: List of quantiles used.
        
    Returns:
        torch.Tensor: Scalar loss value.
    """
    assert preds.shape[1] == len(quantiles), "Preds dimension must match number of quantiles"
    loss = 0.0
    for i, q in enumerate(quantiles):
        errors = target - preds[:, i]
        loss += torch.max((q - 1) * errors, q * errors).mean()
    return loss

# Example usage / wrapper for the system
class PricePredictor:
    def __init__(self, input_dim=10, model_path=None):
        self.model = TimeSeriesTransformer(input_dim=input_dim)
        if model_path:
            self.load_model(model_path)
            
    def predict(self, data: np.ndarray) -> Dict[str, float]:
        """
        Make a prediction based on input data.
        
        Args:
            data (np.ndarray): Input sequence data (seq_len, input_dim)
            
        Returns:
            Dict[str, float]: Forecasted quantiles.
        """
        self.model.eval()
        with torch.no_grad():
            tensor_data = torch.FloatTensor(data).unsqueeze(0) # Add batch dim
            prediction = self.model(tensor_data)
            
            # Assuming quantiles [0.1, 0.5, 0.9]
            return {
                "p10": prediction[0][0].item(),
                "p50": prediction[0][1].item(),
                "p90": prediction[0][2].item()
            }

    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path))
        self.model.eval()

    def save_model(self, path: str):
        torch.save(self.model.state_dict(), path)
