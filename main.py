# Import relevant dependencies
from scripts import region_splitter as rs, \
    crop_splitter as cs, \
    batch_processor as bp, \
    sql_processor as sp, \
    crop_forecaster as cf

# Step 1 -> rs
rs.main()

# Step 2 -> cs
cs.crop_splitter_from_region()

# Step 3 -> bp
bp.batch_processing()

# Step 4 -> sp
sp.sql_processor()

# Step 5 -> cf: Currently runs prediction for ashanti_cassava table only.
cf.crop_forecaster()
