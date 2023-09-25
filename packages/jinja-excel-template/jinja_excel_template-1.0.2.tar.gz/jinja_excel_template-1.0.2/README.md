# Jinja Excel Template Engine

This package can handle some complicated Excel scenarios. It contains:

1. Dynamic sheets based on the data
2. Images are inside the Excel file,
3. Multiple level of grouping in the data (this library does not handle it, but you can have your own data pipeline to prepare the data.),
4. Printing header setting


# Concept
Excel templating is always complicated and normal Excel file does not support them. We have to use an intermediate file named ExcelXML.

Data + Jinja Template ---(Jinja Engine)---> ExcelXML ---(Excel Generator)---> Excel

With Data and Jinja Template, the Jinja Engine can generate the ExcelXML, then the Excel Generator can generate the Excel file. An ExcelXML is an XML representing a single Excel file.

The ExcelXML has a specific format, so the Excel Generator can read it and draw the Excel.

Here is an example of the ExcelXML.

```xml
<Excel>
    <sheet sheetName="myFirstSheet" print_area="A1:L10" print_header="1:3">
        <row> <!-- first row -->
            <cell value="A1" />
            <cell value="A2" />
            <cell value="A3" />
        </row>
        <row /> <!-- second row, empty row -->
        <row> <!-- third row -->
            <cell value="C1" />
            <cell value="C2" />
            <cell value="C3" />
        </row>
    </sheet>
    <sheet sheetName="mySecondSheet" print_area="A1:L10" print_header="1:3">
        <row> <!-- first row -->
            <cell value="A1" />
            <cell value="A2" />
            <cell value="A3" />
        </row>
        <row /> <!-- second row, empty row -->
        <row> <!-- third row -->
            <cell value="C1" />
            <cell value="C2" />
            <cell value="C3" />
        </row>
    </sheet>
</Excel>
```

The Jinja template is to construct the ExcelXML with your own data pipeline.


# Sample
Please check the `tests/countries.py`. It shows the raw data and group countires by region and display countries in multiple sheets. It also contains some basic diagrams.

# Build
```shell
poetry build
```


