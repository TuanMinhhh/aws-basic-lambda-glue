import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.window import Window
from pyspark.sql import functions as F

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

#read data source
s3_file_landing = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/golden_zone/job_detail'
df = spark.read.format('parquet').load(s3_file_landing)


#read dim_table
def read_dim(dim_table):
    s3_file_landing = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/insight_zone/{dim_table}'
    return spark.read.format('parquet').load(s3_file_landing)


dim_city = read_dim('dim_city')
dim_company = read_dim('dim_company')
dim_role = read_dim('dim_role')


#create fact_table
windowSpec = Window.partitionBy().orderBy('deadline')

df_mapping = df.alias('t1') \
               .withColumn('job_id',F.row_number().over(windowSpec)) \
               .withColumn('process_dt', F.current_date()) \
               .join(dim_city.alias('t2'), F.col('t1.city') == F.col('t2.city'), 'left') \
               .join(dim_company.alias('t3'), F.col('t1.company') == F.col('t3.company'), 'left') \
               .join(dim_role.alias('t4'), F.col('t1.role') == F.col('t4.role'), 'left') \
               
               
fact_jobs = df_mapping.select(
                                'job_id',
                                F.col('t4.id').alias('role_id'),
                                F.col('t3.id').alias('company_id'),
                                F.col('t2.id').alias('city_id'),
                                'deadline',
                                'salary',
                                'url',
                                'process_dt'
    )

job_detail = df_mapping.select(
                                'job_id',
                                'job_name',
                                'job_description',
                                'job_requirement',
                                'field',
                                'keywords',
                                'benefit',
                                'location'
    )

#save fact_jobs
s3_saving_path_fact_jobs = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/insight_zone/fact_jobs'
fact_jobs.coalesce(1).write.mode('overwrite').parquet(s3_saving_path_fact_jobs)

#save job_detail
s3_saving_path_job_detail = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/insight_zone/job_detail'
job_detail.coalesce(1).write.mode('overwrite').parquet(s3_saving_path_job_detail)



job.commit()