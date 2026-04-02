{{- define "devops-info.name" -}}
{{- include "common.name" . -}}
{{- end -}}

{{- define "devops-info.fullname" -}}
{{- include "common.fullname" . -}}
{{- end -}}

{{- define "devops-info.labels" -}}
{{- include "common.labels" . -}}
{{- end -}}

{{- define "devops-info.selectorLabels" -}}
{{- include "common.selectorLabels" . -}}
{{- end -}}
