diff --git a/Dockerfile b/Dockerfile
index 7437492..5e9aef7 100644
--- a/Dockerfile
+++ b/Dockerfile
@@ -22,4 +22,6 @@ RUN pip install Cython && pip install tvb-gdist
 # speculative
 RUN pip install pybids siibra requests pyunicore
 
-# RUN pip install mne frites nilearn etc etc
+RUN pip install mne nilearn
+
+RUN apt-get install -y datalad
