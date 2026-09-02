from app.engines.intelligence.data_normalizer import (
    DataNormalizer
)

from app.engines.intelligence.exposure_engine import (
    ExposureEngine
)

from app.engines.intelligence.inference_engine import (
    InferenceEngine
)

from app.engines.intelligence.threat_engine import (
    ThreatEngine
)

from app.engines.intelligence.blast_radius import (
    BlastRadiusEngine
)


class IntelligencePipeline:

    def __init__(self):

        self.normalizer = DataNormalizer()

        self.exposure = ExposureEngine()

        self.inference = InferenceEngine()

        self.threat = ThreatEngine()

        self.blast_radius = BlastRadiusEngine()


    def analyze(self, raw_data):

        data = self.normalizer.normalize(
            raw_data
        )

        exposure_result = (
            self.exposure.analyze(data)
        )

        inference_result = (
            self.inference.analyze(data)
        )

        threat_result = (
            self.threat.analyze(
                exposure_result,
                inference_result
            )
        )

        blast_result = (
            self.blast_radius.calculate(data)
        )

        return {

            "normalized_data": data,

            "exposure": exposure_result,

            "inference": inference_result,

            "threat": threat_result,

            "blast_radius": blast_result
        }