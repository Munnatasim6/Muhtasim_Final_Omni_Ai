import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import logging

logger = logging.getLogger("MarketGAN")

class Generator(nn.Module):
    def __init__(self, latent_dim, output_dim):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(128, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, output_dim),
            nn.Tanh()
        )

    def forward(self, z):
        return self.model(z)

class Discriminator(nn.Module):
    def __init__(self, input_dim):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

class MarketGAN:
    """
    Generative Adversarial Network for Market Simulation.
    Generates fake market data (e.g., Black Swan events) to train robust agents.
    """
    def __init__(self, feature_dim: int = 10, latent_dim: int = 100):
        self.feature_dim = feature_dim
        self.latent_dim = latent_dim
        
        # Check for CUDA
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"MarketGAN initializing on {self.device}")

        self.generator = Generator(latent_dim, feature_dim).to(self.device)
        self.discriminator = Discriminator(feature_dim).to(self.device)

        self.optimizer_G = optim.Adam(self.generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        self.optimizer_D = optim.Adam(self.discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))
        
        self.criterion = nn.BCELoss()

    def train_step(self, real_data: np.ndarray):
        """
        Perform one training step with a batch of real market data.
        """
        batch_size = real_data.shape[0]
        real_data = torch.FloatTensor(real_data).to(self.device)

        # Labels
        valid = torch.ones(batch_size, 1).to(self.device)
        fake = torch.zeros(batch_size, 1).to(self.device)

        # -----------------
        #  Train Generator
        # -----------------
        self.optimizer_G.zero_grad()

        # Sample noise as generator input
        z = torch.randn(batch_size, self.latent_dim).to(self.device)

        # Generate a batch of images
        gen_data = self.generator(z)

        # Loss measures generator's ability to fool the discriminator
        g_loss = self.criterion(self.discriminator(gen_data), valid)

        g_loss.backward()
        self.optimizer_G.step()

        # ---------------------
        #  Train Discriminator
        # ---------------------
        self.optimizer_D.zero_grad()

        # Measure discriminator's ability to classify real from generated samples
        real_loss = self.criterion(self.discriminator(real_data), valid)
        fake_loss = self.criterion(self.discriminator(gen_data.detach()), fake)
        d_loss = (real_loss + fake_loss) / 2

        d_loss.backward()
        self.optimizer_D.step()

        return g_loss.item(), d_loss.item()

    def generate_scenario(self, num_samples: int = 1) -> np.ndarray:
        """
        Generate synthetic market data scenarios.
        """
        with torch.no_grad():
            z = torch.randn(num_samples, self.latent_dim).to(self.device)
            gen_data = self.generator(z).cpu().numpy()
        return gen_data
