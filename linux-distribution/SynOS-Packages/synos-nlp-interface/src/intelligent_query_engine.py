#!/usr/bin/env python3
"""
SynOS Intelligent Query Processing Engine
Advanced query parsing and execution for complex security operations
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum

import spacy
import networkx as nx
from transformers import pipeline, AutoTokenizer, AutoModel
import torch


class QueryType(Enum):
    SIMPLE = "simple"
    COMPOUND = "compound"
    CONDITIONAL = "conditional"
    TEMPORAL = "temporal"
    COMPLEX_WORKFLOW = "complex_workflow"


class ExecutionStrategy(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"


@dataclass
class QueryStep:
    step_id: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    timeout: int = 300
    retry_count: int = 0


@dataclass
class QueryPlan:
    query_id: str
    original_query: str
    query_type: QueryType
    execution_strategy: ExecutionStrategy
    steps: List[QueryStep]
    estimated_time: int
    risk_level: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StepResult:
    step_id: str
    success: bool
    output: Any
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryExecution:
    query_id: str
    query_plan: QueryPlan
    step_results: List[StepResult]
    overall_success: bool
    total_execution_time: float
    start_time: datetime
    end_time: Optional[datetime] = None


class QueryParser:
    """Parse complex natural language queries into executable plans"""

    def __init__(self):
        # Load language model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy model not available")
            self.nlp = None

        # Query pattern templates
        self.query_patterns = {
            # Sequential patterns
            r'scan\s+(.+?)\s+(?:and|then)\s+(.+)': QueryType.COMPOUND,
            r'first\s+(.+?)\s+then\s+(.+)': QueryType.COMPOUND,
            r'after\s+(.+?)\s+do\s+(.+)': QueryType.CONDITIONAL,

            # Conditional patterns
            r'if\s+(.+?)\s+(?:then|do)\s+(.+)': QueryType.CONDITIONAL,
            r'when\s+(.+?)\s+(?:then|do)\s+(.+)': QueryType.CONDITIONAL,
            r'unless\s+(.+?)\s+(?:then|do)\s+(.+)': QueryType.CONDITIONAL,

            # Temporal patterns
            r'every\s+(\d+)\s+(minutes?|hours?|days?)\s+(.+)': QueryType.TEMPORAL,
            r'schedule\s+(.+?)\s+(?:for|at)\s+(.+)': QueryType.TEMPORAL,
            r'monitor\s+(.+?)\s+for\s+(\d+)\s+(minutes?|hours?)': QueryType.TEMPORAL,

            # Complex workflow patterns
            r'workflow:\s*(.+)': QueryType.COMPLEX_WORKFLOW,
            r'pipeline:\s*(.+)': QueryType.COMPLEX_WORKFLOW,
        }

        # Action extraction patterns
        self.action_patterns = {
            'scan': r'\b(?:scan|nmap|check|probe)\s+([^\s,]+)',
            'recon': r'\b(?:recon|reconnaissance|gather|collect)\s+(?:on|about|for)?\s*([^\s,]+)',
            'analyze': r'\b(?:analyze|examine|investigate|correlate)\s+([^\s,]+)',
            'exploit': r'\b(?:exploit|attack|penetrate)\s+([^\s,]+)',
            'report': r'\b(?:report|generate|export|save)\s+(?:to|as)?\s*([^\s,]*)',
            'monitor': r'\b(?:monitor|watch|track|tail)\s+([^\s,]+)',
            'configure': r'\b(?:configure|setup|install|enable|disable)\s+([^\s,]+)',
        }

    def parse_query(self, query: str) -> QueryPlan:
        """Parse natural language query into execution plan"""
        query_id = f"query_{int(datetime.now().timestamp() * 1000)}"

        # Determine query type
        query_type = self._classify_query_type(query)

        # Extract steps based on query type
        if query_type == QueryType.SIMPLE:
            steps = self._parse_simple_query(query)
            strategy = ExecutionStrategy.SEQUENTIAL
        elif query_type == QueryType.COMPOUND:
            steps = self._parse_compound_query(query)
            strategy = ExecutionStrategy.SEQUENTIAL
        elif query_type == QueryType.CONDITIONAL:
            steps = self._parse_conditional_query(query)
            strategy = ExecutionStrategy.CONDITIONAL
        elif query_type == QueryType.TEMPORAL:
            steps = self._parse_temporal_query(query)
            strategy = ExecutionStrategy.PIPELINE
        else:  # COMPLEX_WORKFLOW
            steps = self._parse_complex_workflow(query)
            strategy = ExecutionStrategy.PIPELINE

        # Estimate execution time
        estimated_time = sum(step.timeout for step in steps)

        # Assess risk level
        risk_level = self._assess_risk_level(steps)

        return QueryPlan(
            query_id=query_id,
            original_query=query,
            query_type=query_type,
            execution_strategy=strategy,
            steps=steps,
            estimated_time=estimated_time,
            risk_level=risk_level
        )

    def _classify_query_type(self, query: str) -> QueryType:
        """Classify the type of query"""
        query_lower = query.lower()

        # Check for pattern matches
        for pattern, query_type in self.query_patterns.items():
            if re.search(pattern, query_lower):
                return query_type

        # Check for compound indicators
        compound_indicators = ['and', 'then', 'after', 'followed by', 'next']
        if any(indicator in query_lower for indicator in compound_indicators):
            return QueryType.COMPOUND

        # Check for conditional indicators
        conditional_indicators = ['if', 'when', 'unless', 'provided that']
        if any(indicator in query_lower for indicator in conditional_indicators):
            return QueryType.CONDITIONAL

        # Check for temporal indicators
        temporal_indicators = ['every', 'schedule', 'monitor for', 'continuously', 'regularly']
        if any(indicator in query_lower for indicator in temporal_indicators):
            return QueryType.TEMPORAL

        return QueryType.SIMPLE

    def _parse_simple_query(self, query: str) -> List[QueryStep]:
        """Parse simple single-action query"""
        # Extract primary action
        action, params = self._extract_primary_action(query)

        step = QueryStep(
            step_id="step_001",
            action=action,
            parameters=params,
            timeout=300
        )

        return [step]

    def _parse_compound_query(self, query: str) -> List[QueryStep]:
        """Parse compound multi-action query"""
        steps = []

        # Split on conjunctions
        parts = re.split(r'\s+(?:and|then|after|followed\s+by|next)\s+', query.lower())

        for i, part in enumerate(parts):
            action, params = self._extract_primary_action(part)

            step = QueryStep(
                step_id=f"step_{i+1:03d}",
                action=action,
                parameters=params,
                dependencies=[f"step_{i:03d}"] if i > 0 else [],
                timeout=300
            )
            steps.append(step)

        return steps

    def _parse_conditional_query(self, query: str) -> List[QueryStep]:
        """Parse conditional query with if/when/unless logic"""
        steps = []

        # Extract condition and action
        conditional_patterns = [
            r'if\s+(.+?)\s+then\s+(.+)',
            r'when\s+(.+?)\s+do\s+(.+)',
            r'unless\s+(.+?)\s+then\s+(.+)'
        ]

        condition_text = None
        action_text = None

        for pattern in conditional_patterns:
            match = re.search(pattern, query.lower())
            if match:
                condition_text = match.group(1)
                action_text = match.group(2)
                break

        if condition_text and action_text:
            # Create condition check step
            condition_step = QueryStep(
                step_id="condition_001",
                action="evaluate_condition",
                parameters={"condition": condition_text},
                timeout=60
            )
            steps.append(condition_step)

            # Create action step with condition dependency
            action, params = self._extract_primary_action(action_text)
            action_step = QueryStep(
                step_id="action_001",
                action=action,
                parameters=params,
                dependencies=["condition_001"],
                condition="condition_001.success == True",
                timeout=300
            )
            steps.append(action_step)

        return steps

    def _parse_temporal_query(self, query: str) -> List[QueryStep]:
        """Parse temporal/scheduled queries"""
        steps = []

        # Extract temporal parameters
        temporal_match = re.search(r'every\s+(\d+)\s+(minutes?|hours?|days?)', query.lower())
        schedule_match = re.search(r'for\s+(\d+)\s+(minutes?|hours?)', query.lower())

        if temporal_match:
            interval = int(temporal_match.group(1))
            unit = temporal_match.group(2).rstrip('s')

            # Convert to seconds
            multipliers = {'minute': 60, 'hour': 3600, 'day': 86400}
            interval_seconds = interval * multipliers.get(unit, 60)

            # Extract the action to repeat
            action_text = re.sub(r'every\s+\d+\s+\w+\s+', '', query.lower())
            action, params = self._extract_primary_action(action_text)

            # Create repeating step
            step = QueryStep(
                step_id="temporal_001",
                action="scheduled_action",
                parameters={
                    "action": action,
                    "action_params": params,
                    "interval": interval_seconds,
                    "duration": 3600 if not schedule_match else self._parse_duration(schedule_match)
                },
                timeout=interval_seconds + 60
            )
            steps.append(step)

        return steps

    def _parse_complex_workflow(self, query: str) -> List[QueryStep]:
        """Parse complex workflow queries"""
        steps = []

        # Remove workflow prefix
        workflow_text = re.sub(r'^(?:workflow|pipeline):\s*', '', query.lower())

        # Split into workflow steps (numbered or bulleted)
        step_patterns = [
            r'(\d+)\.\s*(.+?)(?=\d+\.|$)',
            r'[-*]\s*(.+?)(?=[-*]|$)',
            r'step\s*\d+:\s*(.+?)(?=step\s*\d+:|$)'
        ]

        workflow_steps = []
        for pattern in step_patterns:
            matches = re.findall(pattern, workflow_text, re.DOTALL | re.MULTILINE)
            if matches:
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    workflow_steps = [match[1].strip() for match in matches]
                else:
                    workflow_steps = [match.strip() for match in matches]
                break

        # If no structured steps found, split on common delimiters
        if not workflow_steps:
            workflow_steps = re.split(r'[,;]\s*', workflow_text)

        # Create steps from workflow
        for i, step_text in enumerate(workflow_steps):
            action, params = self._extract_primary_action(step_text.strip())

            step = QueryStep(
                step_id=f"workflow_{i+1:03d}",
                action=action,
                parameters=params,
                dependencies=[f"workflow_{i:03d}"] if i > 0 else [],
                timeout=300
            )
            steps.append(step)

        return steps

    def _extract_primary_action(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extract primary action and parameters from text"""
        text = text.strip()

        # Try to match against known action patterns
        for action, pattern in self.action_patterns.items():
            match = re.search(pattern, text)
            if match:
                target = match.group(1) if match.groups() else ""
                params = {"target": target}

                # Extract additional parameters
                params.update(self._extract_additional_params(text))
                return action, params

        # Fallback: use first verb as action
        if self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ == "VERB":
                    return token.lemma_, {"query": text}

        return "execute", {"command": text}

    def _extract_additional_params(self, text: str) -> Dict[str, Any]:
        """Extract additional parameters from query text"""
        params = {}

        # Extract output format
        format_match = re.search(r'\b(?:as|to|in)\s+(json|xml|txt|csv|pdf)\b', text.lower())
        if format_match:
            params['format'] = format_match.group(1)

        # Extract scan type
        if 'stealth' in text.lower() or 'passive' in text.lower():
            params['scan_type'] = 'stealth'
        elif 'aggressive' in text.lower() or 'comprehensive' in text.lower():
            params['scan_type'] = 'aggressive'

        # Extract ports
        port_match = re.search(r'port[s]?\s+(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)', text.lower())
        if port_match:
            params['ports'] = port_match.group(1)

        # Extract time limits
        time_match = re.search(r'(?:within|for)\s+(\d+)\s+(seconds?|minutes?|hours?)', text.lower())
        if time_match:
            value = int(time_match.group(1))
            unit = time_match.group(2).rstrip('s')
            multipliers = {'second': 1, 'minute': 60, 'hour': 3600}
            params['time_limit'] = value * multipliers.get(unit, 1)

        return params

    def _parse_duration(self, match) -> int:
        """Parse duration from regex match"""
        value = int(match.group(1))
        unit = match.group(2).rstrip('s')
        multipliers = {'minute': 60, 'hour': 3600, 'day': 86400}
        return value * multipliers.get(unit, 60)

    def _assess_risk_level(self, steps: List[QueryStep]) -> str:
        """Assess overall risk level of query execution"""
        risk_score = 0

        for step in steps:
            # High-risk actions
            if step.action in ['exploit', 'attack', 'configure']:
                risk_score += 3

            # Medium-risk actions
            elif step.action in ['scan', 'probe']:
                risk_score += 2

            # Check for dangerous parameters
            if 'target' in step.parameters:
                target = step.parameters['target']
                # Internal network ranges are higher risk
                if re.match(r'(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)', target):
                    risk_score += 1

            # Aggressive scan types are higher risk
            if step.parameters.get('scan_type') == 'aggressive':
                risk_score += 1

        if risk_score >= 6:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"


class QueryExecutor:
    """Execute query plans with various strategies"""

    def __init__(self):
        self.active_executions: Dict[str, QueryExecution] = {}

    async def execute_query_plan(self, query_plan: QueryPlan) -> QueryExecution:
        """Execute a query plan using appropriate strategy"""
        execution = QueryExecution(
            query_id=query_plan.query_id,
            query_plan=query_plan,
            step_results=[],
            overall_success=True,
            total_execution_time=0.0,
            start_time=datetime.now()
        )

        self.active_executions[query_plan.query_id] = execution

        try:
            if query_plan.execution_strategy == ExecutionStrategy.SEQUENTIAL:
                await self._execute_sequential(execution)
            elif query_plan.execution_strategy == ExecutionStrategy.PARALLEL:
                await self._execute_parallel(execution)
            elif query_plan.execution_strategy == ExecutionStrategy.CONDITIONAL:
                await self._execute_conditional(execution)
            elif query_plan.execution_strategy == ExecutionStrategy.PIPELINE:
                await self._execute_pipeline(execution)

        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            execution.overall_success = False

        finally:
            execution.end_time = datetime.now()
            execution.total_execution_time = (
                execution.end_time - execution.start_time
            ).total_seconds()

            if query_plan.query_id in self.active_executions:
                del self.active_executions[query_plan.query_id]

        return execution

    async def _execute_sequential(self, execution: QueryExecution):
        """Execute steps sequentially"""
        for step in execution.query_plan.steps:
            if not execution.overall_success:
                break

            result = await self._execute_step(step, execution)
            execution.step_results.append(result)

            if not result.success:
                execution.overall_success = False

    async def _execute_parallel(self, execution: QueryExecution):
        """Execute steps in parallel where possible"""
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(execution.query_plan.steps)

        # Execute in dependency order with parallelization
        executed_steps = set()
        while len(executed_steps) < len(execution.query_plan.steps):
            # Find steps ready to execute
            ready_steps = [
                step for step in execution.query_plan.steps
                if step.step_id not in executed_steps and
                all(dep in executed_steps for dep in step.dependencies)
            ]

            if not ready_steps:
                break

            # Execute ready steps in parallel
            tasks = [self._execute_step(step, execution) for step in ready_steps]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for step, result in zip(ready_steps, results):
                if isinstance(result, Exception):
                    result = StepResult(
                        step_id=step.step_id,
                        success=False,
                        output=None,
                        execution_time=0.0,
                        error_message=str(result)
                    )

                execution.step_results.append(result)
                executed_steps.add(step.step_id)

                if not result.success:
                    execution.overall_success = False

    async def _execute_conditional(self, execution: QueryExecution):
        """Execute steps with conditional logic"""
        step_results = {}

        for step in execution.query_plan.steps:
            # Check if step should be executed based on condition
            should_execute = True

            if step.condition:
                should_execute = self._evaluate_condition(step.condition, step_results)

            if should_execute:
                result = await self._execute_step(step, execution)
                execution.step_results.append(result)
                step_results[step.step_id] = result

                if not result.success:
                    execution.overall_success = False
            else:
                # Create skipped result
                result = StepResult(
                    step_id=step.step_id,
                    success=True,
                    output="Step skipped due to condition",
                    execution_time=0.0,
                    metadata={"skipped": True}
                )
                execution.step_results.append(result)
                step_results[step.step_id] = result

    async def _execute_pipeline(self, execution: QueryExecution):
        """Execute steps in pipeline fashion"""
        pipeline_data = {}

        for step in execution.query_plan.steps:
            # Pass output from previous steps as input
            if step.dependencies:
                for dep_id in step.dependencies:
                    dep_result = next(
                        (r for r in execution.step_results if r.step_id == dep_id),
                        None
                    )
                    if dep_result and dep_result.success:
                        pipeline_data[dep_id] = dep_result.output

            # Add pipeline data to step parameters
            step.parameters['pipeline_input'] = pipeline_data

            result = await self._execute_step(step, execution)
            execution.step_results.append(result)

            if not result.success:
                execution.overall_success = False
                break

            # Store output for next step
            pipeline_data[step.step_id] = result.output

    async def _execute_step(self, step: QueryStep, execution: QueryExecution) -> StepResult:
        """Execute individual step"""
        start_time = datetime.now()

        try:
            # Route to appropriate executor based on action
            if step.action == "scan":
                output = await self._execute_scan(step)
            elif step.action == "recon":
                output = await self._execute_recon(step)
            elif step.action == "analyze":
                output = await self._execute_analyze(step)
            elif step.action == "exploit":
                output = await self._execute_exploit(step)
            elif step.action == "monitor":
                output = await self._execute_monitor(step)
            elif step.action == "report":
                output = await self._execute_report(step)
            elif step.action == "configure":
                output = await self._execute_configure(step)
            elif step.action == "evaluate_condition":
                output = await self._evaluate_condition_step(step)
            elif step.action == "scheduled_action":
                output = await self._execute_scheduled_action(step)
            else:
                output = await self._execute_generic(step)

            execution_time = (datetime.now() - start_time).total_seconds()

            return StepResult(
                step_id=step.step_id,
                success=True,
                output=output,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.error(f"Step {step.step_id} failed: {e}")

            return StepResult(
                step_id=step.step_id,
                success=False,
                output=None,
                execution_time=execution_time,
                error_message=str(e)
            )

    async def _execute_scan(self, step: QueryStep) -> str:
        """Execute scan action"""
        target = step.parameters.get("target", "")
        scan_type = step.parameters.get("scan_type", "default")

        if scan_type == "stealth":
            command = f"synos-security scan --target {target} --policy stealth"
        elif scan_type == "aggressive":
            command = f"synos-security scan --target {target} --policy aggressive"
        else:
            command = f"synos-security scan --target {target}"

        return await self._execute_command(command, step.timeout)

    async def _execute_recon(self, step: QueryStep) -> str:
        """Execute reconnaissance action"""
        target = step.parameters.get("target", "")
        passive = "passive" in step.parameters.get("scan_type", "")

        command = f"synos-security recon --target {target}"
        if passive:
            command += " --passive"

        return await self._execute_command(command, step.timeout)

    async def _execute_analyze(self, step: QueryStep) -> str:
        """Execute analysis action"""
        target = step.parameters.get("target", "")

        if target.startswith("/"):  # File path
            command = f"synos-security correlate --import-file {target}"
        else:
            command = f"synos-security analyze --target {target}"

        return await self._execute_command(command, step.timeout)

    async def _execute_exploit(self, step: QueryStep) -> str:
        """Execute exploit action (with safety checks)"""
        target = step.parameters.get("target", "")

        # This is a high-risk action - only recommend, don't execute
        command = f"synos-security exploit --target {target} --recommend"

        return await self._execute_command(command, step.timeout)

    async def _execute_monitor(self, step: QueryStep) -> str:
        """Execute monitoring action"""
        target = step.parameters.get("target", "")
        duration = step.parameters.get("time_limit", 60)

        command = f"timeout {duration} synos-security monitor --alerts"
        return await self._execute_command(command, step.timeout)

    async def _execute_report(self, step: QueryStep) -> str:
        """Execute report generation"""
        format_type = step.parameters.get("format", "json")
        command = f"synos-security status --format {format_type}"

        return await self._execute_command(command, step.timeout)

    async def _execute_configure(self, step: QueryStep) -> str:
        """Execute configuration action"""
        target = step.parameters.get("target", "")
        command = f"systemctl status {target}"  # Safe status check

        return await self._execute_command(command, step.timeout)

    async def _evaluate_condition_step(self, step: QueryStep) -> bool:
        """Evaluate a condition step"""
        condition = step.parameters.get("condition", "")

        # Simple condition evaluation (could be expanded)
        if "port" in condition and "open" in condition:
            # Extract port number and target
            port_match = re.search(r'port\s+(\d+)', condition)
            target_match = re.search(r'on\s+([^\s]+)', condition)

            if port_match and target_match:
                port = port_match.group(1)
                target = target_match.group(1)

                # Test if port is open
                command = f"nmap -p {port} {target}"
                result = await self._execute_command(command, 30)
                return "open" in result.lower()

        return False

    async def _execute_scheduled_action(self, step: QueryStep) -> str:
        """Execute scheduled/repeated action"""
        action = step.parameters.get("action", "")
        params = step.parameters.get("action_params", {})
        interval = step.parameters.get("interval", 60)
        duration = step.parameters.get("duration", 3600)

        # Create a temporary step for the repeated action
        repeated_step = QueryStep(
            step_id=f"{step.step_id}_repeat",
            action=action,
            parameters=params
        )

        results = []
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < duration:
            try:
                result = await self._execute_step(repeated_step, None)
                results.append(f"[{datetime.now().isoformat()}] {result.output}")

                await asyncio.sleep(interval)
            except Exception as e:
                results.append(f"[{datetime.now().isoformat()}] Error: {e}")
                break

        return "\n".join(results)

    async def _execute_generic(self, step: QueryStep) -> str:
        """Execute generic command"""
        command = step.parameters.get("command", "echo 'No command specified'")
        return await self._execute_command(command, step.timeout)

    async def _execute_command(self, command: str, timeout: int) -> str:
        """Execute system command with timeout"""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return stdout.decode() + stderr.decode()

        except asyncio.TimeoutError:
            return f"Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Command execution error: {str(e)}"

    def _build_dependency_graph(self, steps: List[QueryStep]) -> nx.DiGraph:
        """Build dependency graph for steps"""
        graph = nx.DiGraph()

        for step in steps:
            graph.add_node(step.step_id)
            for dep in step.dependencies:
                graph.add_edge(dep, step.step_id)

        return graph

    def _evaluate_condition(self, condition: str, step_results: Dict[str, StepResult]) -> bool:
        """Evaluate conditional expression"""
        try:
            # Simple condition evaluation
            # This could be expanded with a proper expression parser
            if ".success == True" in condition:
                step_id = condition.split(".")[0]
                return step_results.get(step_id, StepResult("", False, None, 0.0)).success

            return True
        except Exception:
            return False


class IntelligentQueryEngine:
    """Main intelligent query processing engine"""

    def __init__(self, db_path: str = "/var/lib/synos/query_engine.db"):
        self.db_path = Path(db_path)
        self.parser = QueryParser()
        self.executor = QueryExecutor()

        # Query history
        self.query_history: List[QueryExecution] = []

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id TEXT UNIQUE NOT NULL,
                    original_query TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    execution_strategy TEXT NOT NULL,
                    overall_success BOOLEAN NOT NULL,
                    total_execution_time REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    steps_data TEXT,
                    results_data TEXT
                )
            """)
            conn.commit()

    async def process_query(self, query: str) -> QueryExecution:
        """Process intelligent query from natural language to execution"""

        # Parse query into execution plan
        query_plan = self.parser.parse_query(query)

        logging.info(f"Parsed query: {query_plan.query_type.value} strategy with {len(query_plan.steps)} steps")

        # Execute the plan
        execution = await self.executor.execute_query_plan(query_plan)

        # Store execution
        await self._store_execution(execution)

        # Add to history
        self.query_history.append(execution)

        return execution

    async def _store_execution(self, execution: QueryExecution):
        """Store query execution in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO query_executions
                    (query_id, original_query, query_type, execution_strategy,
                     overall_success, total_execution_time, risk_level,
                     start_time, end_time, steps_data, results_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.query_id,
                    execution.query_plan.original_query,
                    execution.query_plan.query_type.value,
                    execution.query_plan.execution_strategy.value,
                    execution.overall_success,
                    execution.total_execution_time,
                    execution.query_plan.risk_level,
                    execution.start_time,
                    execution.end_time,
                    json.dumps([{
                        'step_id': step.step_id,
                        'action': step.action,
                        'parameters': step.parameters,
                        'dependencies': step.dependencies
                    } for step in execution.query_plan.steps]),
                    json.dumps([{
                        'step_id': result.step_id,
                        'success': result.success,
                        'execution_time': result.execution_time,
                        'output_preview': result.output[:500] if result.output else None
                    } for result in execution.step_results])
                ))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to store execution: {e}")

    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """Get intelligent query suggestions"""
        suggestions = []

        partial_lower = partial_query.lower()

        # Sequential workflow suggestions
        if 'scan' in partial_lower:
            suggestions.extend([
                "scan 192.168.1.0/24 and then generate a report",
                "scan target.com for vulnerabilities and analyze results",
                "perform stealth scan on target and correlate with existing data"
            ])

        # Conditional suggestions
        if 'if' in partial_lower or 'when' in partial_lower:
            suggestions.extend([
                "if port 22 is open on target then run SSH security check",
                "when vulnerabilities are found then generate detailed report",
                "if network scan finds hosts then perform service enumeration"
            ])

        # Temporal suggestions
        if 'monitor' in partial_lower or 'every' in partial_lower:
            suggestions.extend([
                "monitor network activity for 30 minutes",
                "every 5 minutes check system status and alert on changes",
                "continuously monitor security logs and correlate threats"
            ])

        # Complex workflow suggestions
        if 'workflow' in partial_lower or 'pipeline' in partial_lower:
            suggestions.extend([
                "workflow: 1. reconnaissance 2. vulnerability scan 3. exploit analysis 4. report",
                "pipeline: gather OSINT -> scan for vulnerabilities -> correlate with threat intel",
                "complete security assessment: recon -> scan -> analyze -> report"
            ])

        return suggestions[:10]

    def get_execution_history(self, limit: int = 20) -> List[QueryExecution]:
        """Get recent query execution history"""
        return self.query_history[-limit:]

    def get_active_executions(self) -> Dict[str, QueryExecution]:
        """Get currently running executions"""
        return self.executor.active_executions.copy()


async def main():
    """Example usage of Intelligent Query Engine"""
    logging.basicConfig(level=logging.INFO)

    engine = IntelligentQueryEngine()

    # Example complex queries
    test_queries = [
        "scan 192.168.1.0/24 and then analyze the results",
        "if port 80 is open on example.com then run a web vulnerability scan",
        "workflow: 1. gather information about target.com 2. scan for vulnerabilities 3. generate report",
        "monitor network activity for 5 minutes and alert on suspicious connections",
        "perform reconnaissance on target.com then scan discovered services and export results as JSON"
    ]

    print("🧠 SynOS Intelligent Query Processing Engine")
    print("=" * 55)

    for query in test_queries:
        print(f"\n🗣️ Query: '{query}'")

        execution = await engine.process_query(query)

        print(f"📋 Query Type: {execution.query_plan.query_type.value}")
        print(f"⚡ Strategy: {execution.query_plan.execution_strategy.value}")
        print(f"🔢 Steps: {len(execution.query_plan.steps)}")
        print(f"🎯 Risk Level: {execution.query_plan.risk_level}")
        print(f"✅ Success: {execution.overall_success}")
        print(f"⏱️ Execution Time: {execution.total_execution_time:.2f}s")

        print("📝 Step Results:")
        for result in execution.step_results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.step_id}: {result.execution_time:.2f}s")

    print(f"\n📊 Total executions in history: {len(engine.get_execution_history())}")


if __name__ == "__main__":
    asyncio.run(main())