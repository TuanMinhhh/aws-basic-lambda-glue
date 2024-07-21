import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

from joblib import variables as V
from pyspark.sql import functions as F

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
print(args)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

s3_file_landing = f's3://{V.DATA_LANDING_BUCKET_NAME}/ynn/payment_type/payment_type.csv'

df = spark.read.option('header', 'true').option('delimiter', ',').csv(s3_file_landing)

s3_saving_path = f's3://{V.DATA_LANDING_BUCKET_NAME}/golden_zone/demo_table'

# logic transforms
df = df.withColumn("type_nm", F.concat(F.col("type_nm"), F.lit(" test")))

df.coalesce(1).write.mode('overwrite').parquet(s3_saving_path)
job.commit()
