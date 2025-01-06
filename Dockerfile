FROM python:3.12

WORKDIR /app

RUN pip install requests pydicom

COPY auto_label.py .

LABEL org.nrg.commands="[{\"name\": \"dcm2mriqc\", \"description\": \"A pipeline designed to run mriqc on DICOMs. Converts DICOMs to BIDS formatted NIFTIs files using dcm2bids, runs MRIQC, outputs MRIQC reports, then deletes intermediate NIFTI files.\", \"version\": \"latest\", \"schema-version\": \"1.0\", \"image\": \"kkurkela92/dcm2mriqc:latest\", \"type\": \"docker\", \"limit-cpu\": \"4\", \"command-line\": \"bash pipeline.sh '#MRIQC_ARGS#'\", \"reserve-memory\": \"10000\", \"override-entrypoint\": true, \"mounts\": [{\"name\": \"in\", \"writable\": false, \"path\": \"/input\"}, {\"name\": \"out\", \"writable\": true, \"path\": \"/output\"}], \"environment-variables\": {}, \"ports\": {}, \"inputs\": [{\"name\": \"mriqc-arguments\", \"description\": \"Arguments to pass to mriqc\", \"type\": \"string\", \"default-value\": \"\", \"required\": false, \"replacement-key\": \"#MRIQC_ARGS#\", \"select-values\": []}], \"outputs\": [{\"name\": \"output\", \"description\": \"Output QC files\", \"required\": true, \"mount\": \"out\"}], \"xnat\": [{\"name\": \"dcm2mriqc - scan\", \"description\": \"Run the dcm2mriqc with a scan mounted\", \"contexts\": [\"xnat:imageScanData\"], \"external-inputs\": [{\"name\": \"scan\", \"description\": \"Input scan\", \"type\": \"Scan\", \"required\": true, \"provides-files-for-command-mount\": \"in\", \"load-children\": false}], \"derived-inputs\": [], \"output-handlers\": [{\"name\": \"output-resource\", \"accepts-command-output\": \"output\", \"as-a-child-of\": \"scan\", \"type\": \"Resource\", \"label\": \"MRIQC\", \"tags\": []}]}], \"container-labels\": {}, \"generic-resources\": {}, \"ulimits\": {}, \"secrets\": []}]"
