---
id: search
title: Search
sidebar_label: Search
---

# Search

The eDiscovery Hypergraph platform provides powerful search capabilities that go beyond simple keyword matching, leveraging AI and hypergraph relationships to find exactly what you need.

## Search Types

### 1. Full-Text Search

Traditional keyword search with advanced operators:

```javascript
// Basic search
"contract agreement"

// Boolean operators
"contract AND (breach OR violation) NOT draft"

// Phrase search
"force majeure clause"

// Proximity search
"payment terms"~10  // Words within 10 positions

// Wildcard search
"confiden*"  // Matches confidential, confidence, etc.

// Fuzzy search
"attorny~"  // Matches attorney with typo tolerance
```

### 2. Semantic Search

AI-powered search that understands meaning and context:

```python
async def semantic_search(query: str, options: SearchOptions) -> SearchResults:
    """
    Perform semantic search using embeddings
    """
    
    # Generate query embedding
    query_embedding = await generate_embedding(query)
    
    # Search in vector database
    results = await vector_db.search(
        embedding=query_embedding,
        top_k=options.limit,
        filters=options.filters,
        include_score=True
    )
    
    # Re-rank with cross-encoder
    if options.rerank:
        results = await rerank_results(query, results)
    
    # Enhance with explanations
    for result in results:
        result.explanation = await explain_relevance(query, result.document)
    
    return SearchResults(
        items=results,
        total=len(results),
        query_understanding=await analyze_query_intent(query)
    )
```

### 3. Entity-Based Search

Find documents related to specific entities:

```graphql
query EntitySearch($entityName: String!, $entityType: EntityType) {
  searchByEntity(name: $entityName, type: $entityType) {
    documents {
      id
      title
      relevanceScore
      entityMentions {
        text
        context
        confidence
      }
    }
    relatedEntities {
      name
      type
      relationshipType
      strength
    }
  }
}
```

### 4. Hypergraph Search

Leverage document relationships for complex queries:

```elixir
defmodule HypergraphSearch do
  @doc """
  Search using hypergraph relationships
  """
  def search(query_params) do
    # Start with seed documents
    seed_docs = find_seed_documents(query_params)
    
    # Expand through hyperedges
    expanded_results = seed_docs
      |> expand_through_hyperedges(query_params.expansion_depth)
      |> filter_by_relevance(query_params.min_relevance)
      |> rank_by_centrality()
    
    # Include relationship paths
    with_paths = Enum.map(expanded_results, fn doc ->
      %{
        document: doc,
        path: find_shortest_path(seed_docs, doc),
        connection_strength: calculate_connection_strength(seed_docs, doc)
      }
    end)
    
    {:ok, with_paths}
  end
end
```

## Advanced Search Features

### 1. Search Templates

Pre-configured searches for common legal queries:

```yaml
templates:
  privilege_review:
    name: "Attorney-Client Privilege Review"
    query: |
      (attorney OR lawyer OR counsel) AND 
      (advice OR opinion OR recommendation) AND
      ("attorney-client" OR "legal advice" OR "privileged")
    filters:
      - type: "email"
      - has_attachments: true
    boost_fields:
      - sender_domain: "lawfirm.com"
      
  contract_breach:
    name: "Contract Breach Investigation"
    query: |
      (breach OR violation OR default) AND
      (contract OR agreement) AND
      (damages OR remedy OR termination)
    date_range: "last_2_years"
    entity_focus: ["parties", "dates", "monetary_amounts"]
```

### 2. Faceted Search

Dynamic filtering with real-time counts:

```typescript
interface SearchFacets {
  documentType: FacetGroup<"email" | "contract" | "memo">;
  dateRange: FacetGroup<DateRange>;
  entities: {
    people: FacetGroup<string>;
    organizations: FacetGroup<string>;
    locations: FacetGroup<string>;
  };
  privilege: FacetGroup<PrivilegeType>;
  sentiment: FacetGroup<"positive" | "negative" | "neutral">;
  language: FacetGroup<string>;
}

// Example faceted search request
const searchRequest = {
  query: "merger acquisition",
  facets: {
    documentType: ["email", "contract"],
    dateRange: {
      start: "2023-01-01",
      end: "2023-12-31"
    },
    entities: {
      organizations: ["Acme Corp", "GlobalTech Inc"]
    }
  },
  sortBy: "relevance",
  limit: 50
};
```

### 3. Search Analytics

Track and analyze search patterns:

```sql
-- Most common search terms
CREATE MATERIALIZED VIEW search_analytics AS
SELECT 
    query_term,
    COUNT(*) as search_count,
    AVG(results_clicked) as avg_clicks,
    AVG(search_duration) as avg_duration,
    COUNT(DISTINCT user_id) as unique_users
FROM search_logs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY query_term
ORDER BY search_count DESC;

-- Search effectiveness
SELECT 
    DATE(created_at) as search_date,
    COUNT(*) as total_searches,
    AVG(CASE WHEN results_clicked > 0 THEN 1 ELSE 0 END) as click_through_rate,
    AVG(results_returned) as avg_results,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY search_duration) as median_duration
FROM search_logs
GROUP BY DATE(created_at)
ORDER BY search_date DESC;
```

### 4. Saved Searches & Alerts

```python
class SavedSearchManager:
    async def create_saved_search(
        self,
        user_id: str,
        search_config: SavedSearchConfig
    ) -> SavedSearch:
        """
        Save a search configuration for reuse and alerts
        """
        saved_search = SavedSearch(
            user_id=user_id,
            name=search_config.name,
            query=search_config.query,
            filters=search_config.filters,
            alert_config=search_config.alert_config,
            created_at=datetime.utcnow()
        )
        
        await self.db.saved_searches.insert_one(saved_search.dict())
        
        # Schedule alert checks if configured
        if search_config.alert_config:
            await self.schedule_alerts(saved_search)
        
        return saved_search
    
    async def check_alerts(self, saved_search: SavedSearch):
        """
        Check for new results matching saved search
        """
        # Get last check timestamp
        last_check = saved_search.last_alert_check or saved_search.created_at
        
        # Search for new documents
        new_results = await self.search_engine.search(
            query=saved_search.query,
            filters={
                **saved_search.filters,
                "created_after": last_check
            }
        )
        
        if new_results.total > 0:
            await self.send_alert(saved_search.user_id, new_results)
        
        # Update last check
        saved_search.last_alert_check = datetime.utcnow()
        await self.db.saved_searches.update_one(
            {"_id": saved_search.id},
            {"$set": {"last_alert_check": saved_search.last_alert_check}}
        )
```

## Search Implementation

### 1. Query Parser

```python
from pyparsing import Word, Literal, QuotedString, Optional, ZeroOrMore

class QueryParser:
    def __init__(self):
        # Define grammar
        self.term = Word(alphanums + "_")
        self.phrase = QuotedString('"')
        self.field_name = Word(alphas)
        self.field_value = self.term | self.phrase
        self.field_search = self.field_name + Literal(":") + self.field_value
        
        self.and_op = Literal("AND")
        self.or_op = Literal("OR")
        self.not_op = Literal("NOT")
        
        self.expression = self.build_expression()
    
    def parse(self, query_string: str) -> QueryAST:
        """
        Parse search query into AST
        """
        try:
            parsed = self.expression.parseString(query_string, parseAll=True)
            return self.build_ast(parsed)
        except ParseException as e:
            raise QueryParseError(f"Invalid query: {e}")
    
    def build_ast(self, parsed_tokens) -> QueryAST:
        """
        Build abstract syntax tree from parsed tokens
        """
        # Implementation details...
        pass
```

### 2. Search Executor

```elixir
defmodule SearchExecutor do
  @moduledoc """
  Executes search queries across multiple backends
  """
  
  def execute(query, options \\ %{}) do
    # Parse query
    {:ok, ast} = QueryParser.parse(query)
    
    # Build search pipeline
    pipeline = [
      &text_search/2,
      &entity_filter/2,
      &date_filter/2,
      &privilege_filter/2,
      &hypergraph_expansion/2,
      &relevance_scoring/2,
      &result_grouping/2
    ]
    
    # Execute pipeline
    results = Enum.reduce(pipeline, {ast, options}, fn stage, {ast, opts} ->
      stage.(ast, opts)
    end)
    
    # Format results
    format_results(results, options)
  end
  
  defp text_search(ast, options) do
    # MongoDB text search
    text_query = build_text_query(ast)
    
    documents = MongoDB.find(:documents, %{
      "$text" => %{"$search" => text_query},
      "$and" => build_filters(options)
    })
    
    {ast, Map.put(options, :documents, documents)}
  end
  
  defp hypergraph_expansion({ast, options}) do
    # Expand search through hypergraph
    documents = options[:documents] || []
    
    expanded = documents
      |> Enum.flat_map(&find_related_documents/1)
      |> Enum.uniq_by(& &1.id)
      |> score_by_relationship_strength(documents)
    
    {ast, Map.put(options, :documents, expanded)}
  end
end
```

### 3. Relevance Scoring

```python
class RelevanceScorer:
    def __init__(self):
        self.weights = {
            "title_match": 3.0,
            "content_match": 1.0,
            "entity_match": 2.0,
            "date_proximity": 1.5,
            "hypergraph_distance": 2.5,
            "user_interaction": 1.2
        }
    
    def score_document(
        self,
        document: Document,
        query: Query,
        context: SearchContext
    ) -> float:
        """
        Calculate multi-factor relevance score
        """
        scores = {}
        
        # Text relevance
        scores["title_match"] = self.calculate_text_score(
            query.terms,
            document.title
        )
        scores["content_match"] = self.calculate_text_score(
            query.terms,
            document.content
        )
        
        # Entity relevance
        if query.entities:
            scores["entity_match"] = self.calculate_entity_score(
                query.entities,
                document.entities
            )
        
        # Temporal relevance
        if query.date_range:
            scores["date_proximity"] = self.calculate_date_score(
                query.date_range,
                document.date
            )
        
        # Graph-based relevance
        if context.use_hypergraph:
            scores["hypergraph_distance"] = self.calculate_graph_score(
                query.seed_documents,
                document
            )
        
        # User behavior signals
        scores["user_interaction"] = self.get_user_signals(
            document.id,
            context.user_id
        )
        
        # Weighted combination
        total_score = sum(
            score * self.weights.get(factor, 1.0)
            for factor, score in scores.items()
        )
        
        return {
            "total": total_score,
            "components": scores,
            "explanation": self.explain_score(scores)
        }
```

## Search UI Components

### 1. Search Bar Component

```typescript
export const AdvancedSearchBar: React.FC = () => {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({});
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  
  // Auto-complete suggestions
  const fetchSuggestions = useDebouncedCallback(async (input: string) => {
    const response = await api.get("/search/suggestions", {
      params: { q: input }
    });
    setSuggestions(response.data);
  }, 300);
  
  // Search history
  const { recentSearches } = useSearchHistory();
  
  return (
    <Box sx={{ position: "relative" }}>
      <TextField
        fullWidth
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          fetchSuggestions(e.target.value);
        }}
        onKeyPress={(e) => {
          if (e.key === "Enter") {
            handleSearch();
          }
        }}
        placeholder="Search documents, entities, or legal concepts..."
        InputProps={{
          startAdornment: <SearchIcon />,
          endAdornment: (
            <IconButton onClick={() => setShowAdvanced(true)}>
              <TuneIcon />
            </IconButton>
          )
        }}
      />
      
      {/* Suggestions dropdown */}
      {suggestions.length > 0 && (
        <Paper sx={{ position: "absolute", top: "100%", width: "100%", mt: 1 }}>
          {suggestions.map((suggestion) => (
            <MenuItem
              key={suggestion.id}
              onClick={() => handleSuggestionClick(suggestion)}
            >
              <ListItemIcon>
                {getSuggestionIcon(suggestion.type)}
              </ListItemIcon>
              <ListItemText
                primary={suggestion.text}
                secondary={suggestion.category}
              />
            </MenuItem>
          ))}
        </Paper>
      )}
    </Box>
  );
};
```

### 2. Search Results Display

```typescript
export const SearchResults: React.FC<SearchResultsProps> = ({ results }) => {
  const [viewMode, setViewMode] = useState<"list" | "grid" | "timeline">("list");
  const [selectedResults, setSelectedResults] = useState<Set<string>>(new Set());
  
  return (
    <Box>
      {/* Results header */}
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">
          {results.total} results found
          {results.searchTime && ` (${results.searchTime}ms)`}
        </Typography>
        
        <Box>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, mode) => setViewMode(mode)}
          >
            <ToggleButton value="list">
              <ListIcon />
            </ToggleButton>
            <ToggleButton value="grid">
              <GridIcon />
            </ToggleButton>
            <ToggleButton value="timeline">
              <TimelineIcon />
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>
      
      {/* Query understanding */}
      {results.queryUnderstanding && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <AlertTitle>Search interpreted as:</AlertTitle>
          {results.queryUnderstanding.explanation}
        </Alert>
      )}
      
      {/* Results list */}
      {viewMode === "list" && (
        <List>
          {results.items.map((result) => (
            <SearchResultItem
              key={result.id}
              result={result}
              selected={selectedResults.has(result.id)}
              onSelect={(selected) => handleSelect(result.id, selected)}
            />
          ))}
        </List>
      )}
      
      {/* Grid view */}
      {viewMode === "grid" && (
        <Grid container spacing={2}>
          {results.items.map((result) => (
            <Grid item xs={12} sm={6} md={4} key={result.id}>
              <SearchResultCard result={result} />
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Timeline view */}
      {viewMode === "timeline" && (
        <TimelineView results={results.items} />
      )}
    </Box>
  );
};
```

## Performance Optimization

### 1. Search Index Optimization

```javascript
// MongoDB index creation
db.documents.createIndex({
  "title": "text",
  "content": "text",
  "metadata.author": "text",
  "processing.results.summary": "text"
}, {
  weights: {
    "title": 10,
    "metadata.author": 5,
    "content": 1
  },
  name: "search_index"
});

// Compound indexes for filtered searches
db.documents.createIndex({
  "caseId": 1,
  "metadata.createdDate": -1,
  "processing.status": 1
});

// Entity search optimization
db.documents.createIndex({
  "processing.results.entities.text": 1,
  "processing.results.entities.type": 1
});
```

### 2. Caching Strategy

```elixir
defmodule SearchCache do
  use GenServer
  
  @ttl :timer.minutes(15)
  
  def get_or_search(query, options) do
    cache_key = generate_cache_key(query, options)
    
    case :ets.lookup(:search_cache, cache_key) do
      [{^cache_key, results, expiry}] when expiry > System.os_time(:millisecond) ->
        {:ok, results}
        
      _ ->
        # Execute search
        {:ok, results} = SearchExecutor.execute(query, options)
        
        # Cache results
        expiry = System.os_time(:millisecond) + @ttl
        :ets.insert(:search_cache, {cache_key, results, expiry})
        
        {:ok, results}
    end
  end
  
  defp generate_cache_key(query, options) do
    :crypto.hash(:sha256, :erlang.term_to_binary({query, options}))
    |> Base.encode16()
  end
end
```

## Next Steps

- Learn about [Compliance Features](/features/compliance)
- Explore [Workflow Automation](/features/workflows)
- Review [REST API](/api/rest-api) for search endpoints
- Check [GraphQL API](/api/graphql-api) for complex queries