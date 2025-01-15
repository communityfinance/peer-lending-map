# About

Shiny app predicting peer-to-peer lending in US Census PUMAs across the country. Developed and maintained by [Community Finance](https://www.communityfi.org).

# Setup

1. Create a virtual environment
2. `pip3 install -r requirements.txt`

# Running the app

```bash
$ shiny run
```

To specify the port, use the `--port` argument. For example:

```bash
$ shiny run --port=[port_number]
```

# Deploying to Shinyapps.io

```bash
rsconnect deploy shiny [path/to/your/app] --name [account-name] --title [your-app-name]
```

# License

[MIT License](https://opensource.org/license/mit)
