<p align="center">
  <img src="./logo.svg" alt="logo" width="142">
</p>

<p align="center">
  <h1 align="center">
    HollowDB Python Client
  </h1>
  <p align="center">
    <i>HollowDB client is the simplest way to use HollowDB, a decentralized & privacy-preserving key-value database.</i>
  </p>


<p align="center">
    <a href="https://opensource.org/licenses/MIT" target="_blank">
        <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-yellow.svg">
    </a>
    <a href="https://docs.hollowdb.xyz" target="_blank">
        <img alt="License: MIT" src="https://img.shields.io/badge/docs-hollowdb-3884FF.svg?logo=gitbook">
    </a>
    <!-- <a href="./.github/workflows/test.yml" target="_blank">
        <img alt="Workflow: Tests" src="https://github.com/firstbatchxyz/hollowdb/actions/workflows/test.yml/badge.svg?branch=master">
    </a>
    <a href="./.github/workflows/build.yml" target="_blank">
        <img alt="Workflow: Styles" src="https://github.com/firstbatchxyz/hollowdb/actions/workflows/build.yml/badge.svg?branch=master">
    </a> -->
    <a href="https://github.com/firstbatchxyz/hollowdb" target="_blank">
        <img alt="GitHub: HollowDB" src="https://img.shields.io/badge/github-hollowdb-5C3EFE?logo=github">
    </a>
    <a href="https://discord.gg/2wuU9ym6fq" target="_blank">
        <img alt="Discord" src="https://dcbadge.vercel.app/api/server/2wuU9ym6fq?style=flat">
    </a>
</p>

## Installation

HollowDB client is an PyPI package. You can install it as:

```sh
pip install hollowdb
```

## Usage

Create a new client with:

```python
from hollowdb import HollowClient

client = HollowClient(api_key="api_key",db="your_db")
```

After that, using the client is as simple as it gets:

```python
# without zero-knowledge proofs
client.get(KEY);
client.put(KEY, VALUE);
client.get_multi([KEY1, KEY2]);
client.update(KEY, VALUE);
client.remove(KEY);
```

If you are connecting to a database that has zero-knowledge proof verifications enabled, you will need to provide proofs along with your requests.

You can use our [HollowDB Prover](https://github.com/firstbatchxyz/hollowdb) utility to generate proofs with minimal development effort. Assuming that a proof is generated for the respective request, the proof shall be provided as an additional argument to these functions.

```python
# with zero-knowledge proofs
client.get(KEY);
client.put(KEY, VALUE);
client.update(KEY, VALUE, PROOF);
client.remove(KEY, PROOF);
```

## Testing

To run tests:

```sh
python -m unittest tests/tests.py
```