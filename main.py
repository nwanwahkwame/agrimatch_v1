# Import relevant dependencies
from scripts import region_splitter as rs, \
    crop_splitter as cs, \
    batch_processor as bp, \
    sql_processor as sp, \
    prophet_training as pt, \
    sanitize_mofa as sm
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings('ignore')

# Step 0 -> sm
# sm.sanitize_mofa()

# Step 1 -> rs
rs.main()

# Step 2 -> cs
cs.crop_splitter_from_region()

# Step 3 -> bp
bp.batch_processing()

# Step 4 -> sp
# sp.sql_processor()

# Step 5 -> cf
# pt.train_all_prophet_models()
