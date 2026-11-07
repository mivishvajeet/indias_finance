"""Incident Management Service: Lifecycle workflow and lineage blast-radius tracing."""
from typing import Any, Dict, List, Optional
import pandas as pd
from data_access.repositories.incident_repository import IncidentRepository
from services.lineage_service import DataLineageService


class IncidentService:
    """Manages operational incident workflows and lineage-based fault impact analysis."""

    @staticmethod
    def get_incident_metrics() -> Dict[str, Any]:
        """Calculates operational metrics across open and resolved incidents."""
        df = IncidentRepository.get_all_incidents()
        if df.empty:
            return {"open": 0, "critical": 0, "resolved": 0, "total": 0}

        open_inc = len(df[df["lifecycle_status"] != "RESOLVED"])
        critical_inc = len(df[(df["severity"] == "CRITICAL") & (df["lifecycle_status"] != "RESOLVED")])
        resolved_inc = len(df[df["lifecycle_status"] == "RESOLVED"])

        return {
            "total": len(df),
            "open": open_inc,
            "critical": critical_inc,
            "resolved": resolved_inc,
        }

    @staticmethod
    def get_blast_radius(affected_table: str) -> Dict[str, Any]:
        """Traces upstream root cause sources and downstream impacted dashboards via lineage."""
        lineage = DataLineageService.get_lineage_graph()
        nodes = lineage["nodes"]
        edges = lineage["edges"]

        clean_name = affected_table.split(".")[-1]
        
        # Upstream sources
        upstreams = []
        for src, tgt in edges:
            if tgt == clean_name:
                upstreams.append(src)

        # Downstream impacted consumers
        downstreams = []
        for src, tgt in edges:
            if src == clean_name:
                downstreams.append(tgt)
                # Second-order downstream
                for s2, t2 in edges:
                    if s2 == tgt and t2 not in downstreams:
                        downstreams.append(t2)

        return {
            "target_table": affected_table,
            "upstream_sources": upstreams or ["Raw External Source"],
            "downstream_impact": downstreams or ["Downstream Analytics Layer"],
        }
