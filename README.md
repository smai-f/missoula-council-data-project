# CDP - Missoula

[![Infrastructure Deployment Status](https://github.com/OpenMontana/missoula-council-data-project/workflows/Infrastructure/badge.svg)](https://github.com/OpenMontana/missoula-council-data-project/actions?query=workflow%3A%22Infrastructure%22)
[![Event Gather](https://github.com/OpenMontana/missoula-council-data-project/actions/workflows/event-gather-pipeline.yml/badge.svg)](https://github.com/OpenMontana/missoula-council-data-project/actions/workflows/event-gather-pipeline.yml)
[![Event Index Pipeline](https://github.com/OpenMontana/missoula-council-data-project/workflows/Event%20Index/badge.svg)](https://github.com/OpenMontana/missoula-council-data-project/actions?query=workflow%3A%22Event+Index%22)
[![Web Deployment Status](https://github.com/OpenMontana/missoula-council-data-project/workflows/Web%20App/badge.svg)](https://OpenMontana.github.io/missoula-council-data-project)
[![Repo Build Status](https://github.com/OpenMontana/missoula-council-data-project/workflows/Build%20Main/badge.svg)](https://github.com/OpenMontana/missoula-council-data-project/actions?query=workflow%3A%22Build+Main%22)

---

## Council Data Project

Council Data Project is an open-source project dedicated to providing journalists, activists, researchers, and all members of each community we serve with the tools they need to stay informed and hold their Council Members accountable.

For more information about Council Data Project, please visit [our website](https://councildataproject.org/).

## Instance Information

This repo serves the municipality: **Missoula**

### Python Access

Install:

`pip install cdp-backend`

Quickstart:

```python
from cdp_backend.database import models as db_models
from cdp_backend.pipeline.transcript_model import Transcript
import fireo
from gcsfs import GCSFileSystem
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client

# Connect to the database
fireo.connection(client=Client(
    project="missoula-council-data-proj",
    credentials=AnonymousCredentials()
))

# Read from the database
five_people = list(db_models.Person.collection.fetch(5))

# Connect to the file store
fs = GCSFileSystem(project="missoula-council-data-proj", token="anon")

# Read a transcript's details from the database
transcript_model = list(db_models.Transcript.collection.fetch(1))[0]

# Read the transcript directly from the file store
with fs.open(transcript_model.file_ref.get().uri, "r") as open_resource:
    transcript = Transcript.from_json(open_resource.read())

# OR download and store the transcript locally with `get`
fs.get(transcript_model.file_ref.get().uri, "local-transcript.json")
# Then read the transcript from your local machine
with open("local-transcript.json", "r") as open_resource:
    transcript = Transcript.from_json(open_resource.read())
```

-   See the [CDP Database Schema](https://councildataproject.org/cdp-backend/database_schema.html)
    for a Council Data Project database schema diagram.
-   See the [FireO documentation](https://octabyte.io/FireO/)
    to learn how to construct queries using CDP database models.
-   See the [GCSFS documentation](https://gcsfs.readthedocs.io/en/latest/index.html)
    to learn how to retrieve files from the file store.

## Contributing

If you wish to contribute to CDP please note that the best method to do so is to contribute to the upstream libraries that compose the CDP Instances themselves. These are detailed below.

-   [cdp-backend](https://github.com/CouncilDataProject/cdp-backend): Contains all the database models, data processing pipelines, and infrastructure-as-code for CDP deployments. Contributions here will be available to all CDP Instances. Entirely written in Python.
-   [cdp-frontend](https://github.com/CouncilDataProject/cdp-frontend): Contains all of the components used by the web apps to be hosted on GitHub Pages. Contributions here will be available to all CDP Instances. Entirely written in TypeScript and React.
-   [cookiecutter-cdp-deployment](https://github.com/CouncilDataProject/cookiecutter-cdp-deployment): The repo used to generate new CDP Instance deployments. Like this repo!
-   [councildataproject.org](https://github.com/CouncilDataProject/councildataproject.github.io): Our landing page! Contributions here should largely be text changes and admin updates.

## Instance Admin Documentation

You can find documentation on how to customize, update, and maintain this CDP instance
in the
[admin-docs directory](https://github.com/OpenMontana/missoula-council-data-project/tree/main/admin-docs).

## License

CDP software is licensed under a [MIT License](./LICENSE).

Content produced by this instance is available under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
