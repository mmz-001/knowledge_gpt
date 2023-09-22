<h1 align="center">
📖Berend-Botje - De Lesplanner
</h1>

<div id="top" align="center">
Waarom moeilijk doen ....?
</div>

** Maak lesplannen op basis van de toegevoegde documenten. **


[Demo](https://berend-bot-knowledgegpt.streamlit.app/)

## Berend-Botje 

Doel

### Berend-Botje werkt met Skills

### In deze app demonstreren Berend's skill - Lesplannen

Run the following commands to build and run the Docker image.

```bash
cd knowledge_gpt
docker build -t knowledge_gpt .
docker run -p 8501:8501 knowledge_gpt
```

Open http://localhost:8501 in your browser to access the app.

## Customization

You can increase the max upload file size by changing `maxUploadSize` in `.streamlit/config.toml`.
Currently, the max upload size is 25MB for the hosted version.

## Roadmap

- Add support for more formats (e.g. webpages, PPTX, etc.)
- Highlight relevant phrases in citations
- Support scanned documents with OCR
- More customization options (e.g. chain type, chunk size, etc.)
- Visual PDF viewer
- Support for Local LLMs

## Contributing

All contributions are welcome!

## Contributors

Big thanks to the following people for their contributions!

## License

Distributed under the MIT License. See [LICENSE](https://github.com/mmz-001/knowledge_gpt/blob/main/LICENSE) for more information.

