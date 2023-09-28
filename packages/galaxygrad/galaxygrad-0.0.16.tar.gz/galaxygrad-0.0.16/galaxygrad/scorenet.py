import jax.random as jr
import equinox as eqx
from .models_eqx import ScoreNet
import os

# model params
patch_size=4
hidden_size=64
mix_patch_size=512
mix_hidden_size=512
num_blocks=4
t1=10.0

# noise -- time schedule
int_beta = lambda t: t  

# rng numbers 
key = jr.PRNGKey(42)
model_key, train_key, loader_key, sample_key = jr.split(key, 4)

# initialise model for 64 res
data_shape = (1, 64, 64)
model64 = ScoreNet(
        data_shape,
        patch_size,
        hidden_size,
        mix_patch_size,
        mix_hidden_size,
        num_blocks,
        t1,
        key=model_key,
)

# load 64 res model
FN = os.path.join(os.path.dirname(__file__), 'eqx_hsc_ScoreNet64.eqx')
HSC_ScoreNet64 = eqx.tree_deserialise_leaves(FN, model64)

# initialise model for 32 res
data_shape = (1, 32, 32)
model32 = ScoreNet(
        data_shape,
        patch_size,
        hidden_size,
        mix_patch_size,
        mix_hidden_size,
        num_blocks,
        t1,
        key=model_key,
)

# load 32 res model
FN = os.path.join(os.path.dirname(__file__), 'eqx_hsc_ScoreNet32.eqx')
HSC_ScoreNet32 = eqx.tree_deserialise_leaves(FN, model32)

# initialise model for 32 res
data_shape = (1, 40, 40)
model32 = ScoreNet(
        data_shape,
        patch_size,
        hidden_size,
        mix_patch_size,
        mix_hidden_size,
        num_blocks,
        t1,
        key=model_key,
)

# load 32 res model
FN = os.path.join(os.path.dirname(__file__), 'eqx_ZTF_ScoreNet40.eqx')
ZTF_ScoreNet40 = eqx.tree_deserialise_leaves(FN, model32)

# initialise model for 64 res
data_shape = (1, 64, 64)
model64 = ScoreNet(
        data_shape,
        patch_size,
        hidden_size,
        mix_patch_size,
        mix_hidden_size,
        num_blocks,
        t1,
        key=model_key,
)

# load 64 res model
FN = os.path.join(os.path.dirname(__file__), 'eqx_hsc_LogNet64.eqx')
HSC_LogNet64 = eqx.tree_deserialise_leaves(FN, model64)

# initialise model for 32 res
data_shape = (1, 32, 32)
model32 = ScoreNet(
        data_shape,
        patch_size,
        hidden_size,
        mix_patch_size,
        mix_hidden_size,
        num_blocks,
        t1,
        key=model_key,
)

# load 32 res model
FN = os.path.join(os.path.dirname(__file__), 'eqx_hsc_LogNet32.eqx')
HSC_LogNet32 = eqx.tree_deserialise_leaves(FN, model32)

# initialise model for 32 res
data_shape = (1, 40, 40)
model32 = ScoreNet(
        data_shape,
        patch_size,
        hidden_size,
        mix_patch_size,
        mix_hidden_size,
        num_blocks,
        t1,
        key=model_key,
)

# load 32 res model
FN = os.path.join(os.path.dirname(__file__), 'eqx_ZTF_LogNet40.eqx')
ZTF_LogNet40 = eqx.tree_deserialise_leaves(FN, model32)
