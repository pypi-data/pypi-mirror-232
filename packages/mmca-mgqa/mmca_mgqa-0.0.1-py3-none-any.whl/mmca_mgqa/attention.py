from torch import nn 
from mqga import MGQA

class SimpleMMCA(nn.Module):
    def __init__(
        self,
        dim,
        heads,
    ):
        super().__init__()
        
        self.self_attn = nn.MultiheadAttention(
            embed_dim=dim, 
            num_heads=heads
        )
        
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=dim, 
            num_heads=heads
        )
    
    def forward(self, v, t):
        #self attention for visual tokens
        v = self.self_attn(v, v, v)[0]

        #cross attention for textual tokens
        t = self.cross_attn(t, t, t)[0] + self.cross_attn(t, v, v)[0]

        return t