import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.window import Window

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


#read from golden_zone
s3_file_landing = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/golden_zone/job_detail'
df = spark.read.format('parquet').load(s3_file_landing)

#create_dim_table
def create_dim(column_name):
    a = df.select(column_name).distinct()
    windowSpec = Window.partitionBy().orderBy(column_name)
    result = a.withColumn('id',F.row_number().over(windowSpec)).select('id',column_name)
    
    s3_saving_path = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/insight_zone/dim_{column_name}'
    result.coalesce(1).write.mode('overwrite').parquet(s3_saving_path)
    
#write to s3 bucket
create_dim('role')
create_dim('company')
create_dim('city')
    

job.commit()