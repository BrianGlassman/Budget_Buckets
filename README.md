# Budget_Buckets
Budgeting tool that focuses on continuous operation rather than month-by-month discrete units


## Details
BaseLib/CategoryList is the list of all possible categories (imported to various places)

Order of operations:
1. Loading - loads any external files and converts to a usable format. Makes configuration settings and JSON paths available to downstream processes.
2. PreProcessLogs - handle original/override/final Log logic
3. Categorize - categorize transactions
4. Aggregate - turn Logs into Aggregates
5. Buckets
    1. fetch Aggregates information for Buckets
    2. perform Bucket month logic


- Validation - testing and validation (duh)
    - `Excel --> JSON` pipeline is implicitly validated by git diff

```mermaid
flowchart TD;
    i1[("Excel File(s)")];

    i1 --> Loading;
    
    subgraph Loading;
        direction LR;
        l1[[OpenExcel]];
        l2[[ExcelToJSON]];
        l3[(JSON)];

        l1 --excel_path--> l2;
        l1 --sheets--> l2;
        
        l2 --user input JSONs--> l3;
        l2 --validation JSONs--> l3;
    end;

    Loading --user input JSONs--> p1[[PreProcessLogs]];
    p1 --> c1[[Categorize]];
    c1 --> a1[[Aggregate]];
    a1 --> Buckets;

    subgraph Buckets;
        direction LR;
    end;
```