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

"""Wordcab API Transcript object."""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TranscriptUtterance:
    """Transcript utterance object."""

    text: str
    speaker: str
    end: Optional[str] = field(default=None)
    end_index: Optional[int] = field(default=None)
    start: Optional[str] = field(default=None)
    start_index: Optional[int] = field(default=None)
    timestamp_end: Optional[int] = field(default=None)
    timestamp_start: Optional[int] = field(default=None)


@dataclass
class BaseTranscript:
    """Transcript object."""

    transcript_id: str
    job_id_set: List[str] = field(default_factory=list)
    summary_id_set: List[str] = field(default_factory=list)
    transcript: List[TranscriptUtterance] = field(default_factory=list)
    speaker_map: Dict[str, str] = field(default_factory=dict)
    question_answers: Optional[List[Dict[str, str]]] = field(default=None)

    def __post_init__(self) -> None:
        """Post-init method."""
        if self.speaker_map:
            for key, val in self.speaker_map.items():
                if not isinstance(key, str):
                    raise TypeError(
                        "BaseTranscript.speaker_map keys must be strings, not"
                        f" {type(key)}"
                    )
                if not isinstance(val, str):
                    raise TypeError(
                        "BaseTranscript.speaker_map values must be strings, not"
                        f" {type(val)}"
                    )

    def update_speaker_map(self, speaker_map: Dict[str, str]) -> None:
        """Update the speaker map for the transcript."""
        self.speaker_map = speaker_map


@dataclass
class ListTranscripts:
    """List transcripts object."""

    page_count: int
    next_page: str
    results: List[BaseTranscript]
