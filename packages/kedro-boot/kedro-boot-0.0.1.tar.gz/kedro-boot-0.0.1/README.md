`Kedro Boot` is a framework that streamlines the integration of Kedro projects with various applications. It serves as a bridge that shape the interactions between an application and Kedro's resources

The integration can be performed in two modes : 

1. **Embedded Mode :** This mode involves using Kedro Boot to embed an application inside a Kedro project, leveraging kedro's entry points, session and config loader for managing application lifecycle.
	It's suitable for use cases when the application is lightweight and yet to be developed by a team that already invest in kedro architecture.
	
2. **Standalone Mode :** This mode refers to using Kedro Boot in an external application that has its own entry point. In this case, the external application interacts with Kedro resources through Kedro Boot. It's suitable for large application that already exist before the kedro project, and may have been developed by a different team (like the case of this issue: A Datarobot app that need to run dynamically some kedro pipelines)

In both modes the application can perform multiple pipeline runs with dynamically rendered catalog.

**Example of usages :**
* REST API that trigger pipeline runs
* REST API leveraging kedro boot for App lifecycle and business logic authoring. The API may have POST endpoints with Body Data and may manage resources from backend databases.
* A streamlit or dash app that consume kedro pipelines to perform some calculus.
* Running multiple instances of a monte carlo simulation using a range of parameters.
* A Spark App that parallelize the processign of a large number of unstructured objetcs loaded as SparkRDD and procecced using the pipeline
* Etc ...

This let data scientists concentrate in the business logic (analytics, ML, scientific compute, ..) while having a way to distribute their work as a ready to consume "function" to be integrated in a wider App/system by Engineers (DE/SWE)