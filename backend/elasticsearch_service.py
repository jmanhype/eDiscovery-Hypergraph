"""
Elasticsearch service for full-text search
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import logging

from models import Document, Case, Entity

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for managing Elasticsearch operations"""
    
    def __init__(self):
        self.es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        self.client = AsyncElasticsearch(
            [self.es_url],
            basic_auth=None,  # Add auth if needed
            verify_certs=False
        )
        
    async def initialize(self):
        """Initialize Elasticsearch indices"""
        try:
            # Check if Elasticsearch is available
            info = await self.client.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")
            
            # Create indices
            await self._create_documents_index()
            await self._create_cases_index()
            await self._create_entities_index()
            
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch: {e}")
            raise
    
    async def close(self):
        """Close Elasticsearch client"""
        await self.client.close()
    
    async def _create_documents_index(self):
        """Create documents index with proper mappings"""
        index_name = "ediscovery_documents"
        
        # Check if index exists
        if await self.client.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
            return
        
        # Create index with mappings
        mappings = {
            "properties": {
                "id": {"type": "keyword"},
                "case_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "source": {"type": "keyword"},
                "author": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "status": {"type": "keyword"},
                "privilege_type": {"type": "keyword"},
                "has_significant_evidence": {"type": "boolean"},
                "summary": {"type": "text"},
                "tags": {"type": "keyword"},
                "entities": {
                    "type": "nested",
                    "properties": {
                        "name": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "frequency": {"type": "integer"}
                    }
                },
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
        
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "custom_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "stop", "snowball"]
                    }
                }
            }
        }
        
        await self.client.indices.create(
            index=index_name,
            mappings=mappings,
            settings=settings
        )
        logger.info(f"Created index {index_name}")
    
    async def _create_cases_index(self):
        """Create cases index with proper mappings"""
        index_name = "ediscovery_cases"
        
        if await self.client.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
            return
        
        mappings = {
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "description": {"type": "text"},
                "status": {"type": "keyword"},
                "client_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "case_type": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        }
        
        await self.client.indices.create(
            index=index_name,
            mappings=mappings
        )
        logger.info(f"Created index {index_name}")
    
    async def _create_entities_index(self):
        """Create entities index with proper mappings"""
        index_name = "ediscovery_entities"
        
        if await self.client.indices.exists(index=index_name):
            logger.info(f"Index {index_name} already exists")
            return
        
        mappings = {
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "entity_type": {"type": "keyword"},
                "frequency": {"type": "integer"},
                "document_ids": {"type": "keyword"},
                "case_ids": {"type": "keyword"},
                "first_seen": {"type": "date"},
                "last_seen": {"type": "date"}
            }
        }
        
        await self.client.indices.create(
            index=index_name,
            mappings=mappings
        )
        logger.info(f"Created index {index_name}")
    
    async def index_document(self, document: Document):
        """Index a single document"""
        doc_dict = document.model_dump()
        doc_dict['id'] = str(doc_dict.pop('_id', document.id))
        
        # Convert datetime objects to ISO format
        for field in ['created_at', 'updated_at']:
            if field in doc_dict and doc_dict[field]:
                doc_dict[field] = doc_dict[field].isoformat()
        
        await self.client.index(
            index="ediscovery_documents",
            id=doc_dict['id'],
            document=doc_dict
        )
    
    async def index_case(self, case: Case):
        """Index a single case"""
        case_dict = case.model_dump()
        case_dict['id'] = str(case_dict.pop('_id', case.id))
        
        # Convert datetime objects to ISO format
        for field in ['created_at', 'updated_at']:
            if field in case_dict and case_dict[field]:
                case_dict[field] = case_dict[field].isoformat()
        
        await self.client.index(
            index="ediscovery_cases",
            id=case_dict['id'],
            document=case_dict
        )
    
    async def index_entity(self, entity: Entity):
        """Index a single entity"""
        entity_dict = entity.model_dump()
        entity_dict['id'] = str(entity_dict.pop('_id', entity.id))
        
        # Convert datetime objects to ISO format
        for field in ['first_seen', 'last_seen']:
            if field in entity_dict and entity_dict[field]:
                entity_dict[field] = entity_dict[field].isoformat()
        
        await self.client.index(
            index="ediscovery_entities",
            id=entity_dict['id'],
            document=entity_dict
        )
    
    async def bulk_index_documents(self, documents: List[Document]):
        """Bulk index multiple documents"""
        actions = []
        for doc in documents:
            doc_dict = doc.model_dump()
            doc_dict['id'] = str(doc_dict.pop('_id', doc.id))
            
            # Convert datetime objects to ISO format
            for field in ['created_at', 'updated_at']:
                if field in doc_dict and doc_dict[field]:
                    doc_dict[field] = doc_dict[field].isoformat()
            
            actions.append({
                "_index": "ediscovery_documents",
                "_id": doc_dict['id'],
                "_source": doc_dict
            })
        
        if actions:
            await async_bulk(self.client, actions)
            logger.info(f"Bulk indexed {len(actions)} documents")
    
    async def search_documents(
        self,
        query: str,
        case_id: Optional[str] = None,
        status: Optional[str] = None,
        privilege_type: Optional[str] = None,
        has_significant_evidence: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        from_: int = 0,
        size: int = 25
    ) -> Dict[str, Any]:
        """Search documents with advanced filtering"""
        
        # Build the query
        must_clauses = []
        filter_clauses = []
        
        # Full-text search query
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content", "summary^2", "author"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        # Filters
        if case_id:
            filter_clauses.append({"term": {"case_id": case_id}})
        
        if status:
            filter_clauses.append({"term": {"status": status}})
        
        if privilege_type:
            filter_clauses.append({"term": {"privilege_type": privilege_type}})
        
        if has_significant_evidence is not None:
            filter_clauses.append({"term": {"has_significant_evidence": has_significant_evidence}})
        
        if tags:
            filter_clauses.append({"terms": {"tags": tags}})
        
        # Build the final query
        body = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            },
            "from": from_,
            "size": size,
            "sort": [
                {"_score": {"order": "desc"}},
                {"created_at": {"order": "desc"}}
            ],
            "highlight": {
                "fields": {
                    "content": {"fragment_size": 150, "number_of_fragments": 3},
                    "summary": {"fragment_size": 150, "number_of_fragments": 1}
                }
            }
        }
        
        # Execute search
        response = await self.client.search(
            index="ediscovery_documents",
            body=body
        )
        
        return response
    
    async def search_cases(
        self,
        query: str,
        status: Optional[str] = None,
        case_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        from_: int = 0,
        size: int = 25
    ) -> Dict[str, Any]:
        """Search cases"""
        
        must_clauses = []
        filter_clauses = []
        
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description", "client_name^2"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        if status:
            filter_clauses.append({"term": {"status": status}})
        
        if case_type:
            filter_clauses.append({"term": {"case_type": case_type}})
        
        if tags:
            filter_clauses.append({"terms": {"tags": tags}})
        
        body = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            },
            "from": from_,
            "size": size,
            "sort": [
                {"_score": {"order": "desc"}},
                {"created_at": {"order": "desc"}}
            ]
        }
        
        response = await self.client.search(
            index="ediscovery_cases",
            body=body
        )
        
        return response
    
    async def search_entities(
        self,
        query: str,
        entity_type: Optional[str] = None,
        min_frequency: int = 1,
        from_: int = 0,
        size: int = 50
    ) -> Dict[str, Any]:
        """Search entities"""
        
        must_clauses = []
        filter_clauses = []
        
        if query:
            must_clauses.append({
                "match": {
                    "name": {
                        "query": query,
                        "fuzziness": "AUTO"
                    }
                }
            })
        
        if entity_type:
            filter_clauses.append({"term": {"entity_type": entity_type}})
        
        filter_clauses.append({"range": {"frequency": {"gte": min_frequency}}})
        
        body = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "filter": filter_clauses
                }
            },
            "from": from_,
            "size": size,
            "sort": [
                {"frequency": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ]
        }
        
        response = await self.client.search(
            index="ediscovery_entities",
            body=body
        )
        
        return response
    
    async def suggest_search_terms(self, prefix: str, field: str = "content") -> List[str]:
        """Get search term suggestions based on prefix"""
        body = {
            "suggest": {
                "text-suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": f"{field}.keyword",
                        "size": 10
                    }
                }
            }
        }
        
        response = await self.client.search(
            index="ediscovery_documents",
            body=body
        )
        
        suggestions = []
        if 'suggest' in response and 'text-suggest' in response['suggest']:
            for suggestion in response['suggest']['text-suggest'][0]['options']:
                suggestions.append(suggestion['text'])
        
        return suggestions
    
    async def get_aggregations(self, index: str, field: str) -> Dict[str, int]:
        """Get aggregations for a specific field"""
        body = {
            "size": 0,
            "aggs": {
                "field_counts": {
                    "terms": {
                        "field": field,
                        "size": 100
                    }
                }
            }
        }
        
        response = await self.client.search(index=index, body=body)
        
        aggregations = {}
        if 'aggregations' in response and 'field_counts' in response['aggregations']:
            for bucket in response['aggregations']['field_counts']['buckets']:
                aggregations[bucket['key']] = bucket['doc_count']
        
        return aggregations


# Global instance
es_service = ElasticsearchService()