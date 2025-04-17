FROM python:3.12

WORKDIR /app

RUN pip install requests pydicom

# dcm2niix
ARG D2N_PREFIX="/sw/apps/dcm2niix"
ARG D2N_URI="https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20241211/dcm2niix_lnx.zip"
RUN mkdir -p $D2N_PREFIX && \
    curl -sL $D2N_URI -o $D2N_PREFIX/dcm2niix_lnx.zip && \
    unzip $D2N_PREFIX/dcm2niix_lnx.zip -d $D2N_PREFIX && \
    rm $D2N_PREFIX/dcm2niix_lnx.zip

# adding installation to path
ENV PATH="${D2N_PREFIX}:${PATH}"

# edit this to force recopy of auto_label.py file
RUN echo "04/14/2025"
COPY auto_label.py .

ENTRYPOINT python auto_label.py --user XNAT_USER --host XNAT_HOST --password XNAT_PASS --dicom_dir /dcmdir --project PROJ_ID --subject SUBJ_ID --experiment SESS_ID --scan SCAN_ID

LABEL org.nrg.commands="[{\"name\": \"auto_label\", \"label\": \"auto_label\", \"description\": \"Automatically labels incoming scans\", \"version\": \"1.0\", \"schema-version\": \"1.0\", \"image\": \"kkurkela92/auto_label:latest\", \"type\": \"docker\", \"command-line\": \"python auto_label.py --host \$XNAT_HOST --user \$XNAT_USER --pass \$XNAT_PASS --dicomdir /in --project #PROJ_ID# --subject #SUBJ_ID# --experiment #SESS_ID# --scan #SCAN_ID# --qcmapjson \", \"override-entrypoint\": true, \"mounts\": [{\"name\": \"in\", \"writable\": false, \"path\": \"/input\"}], \"environment-variables\": {}, \"ports\": {}, \"inputs\": [{\"name\": \"SUBJ_ID\", \"description\": \"Subject ID\", \"type\": \"string\", \"required\": true, \"select-values\": []}, {\"name\": \"SESS_ID\", \"description\": \"Session ID\", \"type\": \"string\", \"required\": true, \"select-values\": []}, {\"name\": \"PROJ_ID\", \"description\": \"Project\", \"type\": \"string\", \"required\": true, \"select-values\": []}, {\"name\": \"SCAN_ID\", \"description\": \"Scan ID\", \"type\": \"string\", \"required\": true, \"select-values\": []}], \"outputs\": [], \"xnat\": [{\"name\": \"autolabel-scan\", \"label\": \"Autolabel Scan\", \"description\": \"Run the auto_labeler container with a scan mounted\", \"contexts\": [\"xnat:imageScanData\"], \"external-inputs\": [{\"name\": \"scan\", \"description\": \"Input scan\", \"type\": \"Scan\", \"required\": true, \"provides-files-for-command-mount\": \"in\", \"load-children\": false}], \"derived-inputs\": [{\"name\": \"session\", \"type\": \"Session\", \"required\": true, \"load-children\": false, \"derived-from-wrapper-input\": \"scan\", \"multiple\": false}, {\"name\": \"session-id\", \"type\": \"string\", \"required\": true, \"provides-value-for-command-input\": \"SESS_ID\", \"load-children\": true, \"derived-from-wrapper-input\": \"scan\", \"derived-from-xnat-object-property\": \"id\", \"multiple\": false}, {\"name\": \"session-label\", \"type\": \"string\", \"required\": true, \"provides-value-for-command-input\": \"SESS_LABEL\", \"load-children\": true, \"derived-from-wrapper-input\": \"session\", \"derived-from-xnat-object-property\": \"label\", \"multiple\": false}, {\"name\": \"subject-id\", \"type\": \"string\", \"required\": true, \"provides-value-for-command-input\": \"SUBJ_ID\", \"load-children\": true, \"derived-from-wrapper-input\": \"session\", \"derived-from-xnat-object-property\": \"subject-id\", \"multiple\": false}, {\"name\": \"project\", \"type\": \"string\", \"required\": true, \"provides-value-for-command-input\": \"PROJ_ID\", \"load-children\": true, \"derived-from-wrapper-input\": \"session\", \"derived-from-xnat-object-property\": \"project-id\", \"multiple\": false}, {\"name\": \"scan-id\", \"type\": \"string\", \"required\": true, \"provides-value-for-command-input\": \"SCAN_ID\", \"load-children\": true, \"derived-from-wrapper-input\": \"scan\", \"derived-from-xnat-object-property\": \"id\", \"multiple\": false}], \"output-handlers\": []}], \"container-labels\": {}, \"generic-resources\": {}, \"ulimits\": {}, \"secrets\": []}]"
