# RFC to Requirements

Generate list of requirements from rfc id.

All requirements are categorized as per RFC keywords MUST, MAY etc...

### Install required modules

```
pip3 install -r ./requirements.txt

```

### Usage

```
python3 rfcparser <rfcid>
```

### Output formats

- rfc<id>.txt plain text RFC
- rfc<id>.html requirements table in html format from given rfc
- rfc<id>.csv requirements table in csv format from given rfc

### Limitations

Old rfc ids without xml files may not work as expected.

### Contribution

Please raise PR with your fixes or improvements

