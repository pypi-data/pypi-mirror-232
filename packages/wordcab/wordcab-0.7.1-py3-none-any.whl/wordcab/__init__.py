# Copyright 2022-2023 The Wordcab Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Wordcab Python SDK."""

from .api import (
    change_speaker_labels,
    delete_job,
    get_stats,
    list_jobs,
    list_summaries,
    list_transcripts,
    request,
    retrieve_job,
    retrieve_summary,
    retrieve_transcript,
    start_extract,
    start_summary,
    start_transcription,
)
from .client import Client
from .login import get_token, login

__all__ = [
    "Client",
    "change_speaker_labels",
    "delete_job",
    "get_stats",
    "get_token",
    "list_jobs",
    "list_summaries",
    "list_transcripts",
    "login",
    "request",
    "retrieve_job",
    "retrieve_summary",
    "retrieve_transcript",
    "start_extract",
    "start_summary",
    "start_transcription",
]

__version__ = "0.7.1"
