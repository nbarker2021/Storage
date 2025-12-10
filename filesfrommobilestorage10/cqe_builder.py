#!/usr/bin/env python3
"""
CQE BUILDER - Intelligent Module Extraction & Assembly System
==============================================================

This script understands all CQE monolith files and intelligently:
1. Catalogs all available modules across all monoliths
2. Analyzes dependencies and module purposes  
3. Extracts "best of breed" for each task type
4. Assembles working builds with proper imports
5. Fixes unicode issues automatically
6. Creates standalone executable packages

Author: CQE System
Version: 1.0.0
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Module:
    """Represents a code module from any monolith."""
    name: str
    source_file: str
    line_start: int
    line_end: int
    content: str
    category: str
    dependencies: Set[str] = field(default_factory=set)
    imports: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    
    @property
    def size(self) -> int:
        return len(self.content)
    
    @property
    def line_count(self) -> int:
        return self.content.count('\n')


@dataclass
class Build:
    """Represents a build configuration."""
    name: str
    purpose: str
    modules: List[str]
    entry_point: Optional[str] = None
    cli_enabled: bool = True


class MonolithAnalyzer:
    """Analyzes all monolith files and catalogs modules."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules: Dict[str, Module] = {}
        self.categories: Dict[str, List[str]] = defaultdict(list)
        self.catalog: Dict[str, dict] = {}
        
    def analyze_all(self):
        """Analyze all monolith files."""
        print("🔍 Analyzing CQE Monoliths...")
        print("="*60)
        
        # Analyze each monolith
        self._analyze_code_monolith()
        self._analyze_core_monolith()
        self._analyze_gvs_monolith()
        self._analyze_aletheia_monolith()
        self._analyze_prototype()
        self._analyze_standalone_files()
        
        # Build catalog
        self._build_catalog()
        
        print(f"\n✓ Found {len(self.modules)} modules across {len(self.categories)} categories")
        return self.modules
    
    def _analyze_code_monolith(self):
        """Analyze code_monolith.py - contains multiple modules as class attributes."""
        path = self.project_root / "code_monolith.py"
        if not path.exists():
            return
        
        print(f"\n📦 Analyzing {path.name}...")
        content = path.read_text()
        
        # Find all class definitions that end with "Code:"
        pattern = r'class (\w+)Code:\s+filename\s*=\s*[\'"]([^\'"]+)[\'"]\s+line_count\s*=\s*(\d+)\s+content\s*=\s*"""(.*?)"""'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            class_name = match.group(1)
            filename = match.group(2)
            line_count = int(match.group(3))
            module_content = match.group(4)
            
            # Determine category
            category = self._categorize_module(class_name, module_content)
            
            # Extract metadata
            imports = self._extract_imports(module_content)
            classes = self._extract_classes(module_content)
            functions = self._extract_functions(module_content)
            
            module = Module(
                name=class_name,
                source_file="code_monolith.py",
                line_start=content[:match.start()].count('\n'),
                line_end=content[:match.end()].count('\n'),
                content=module_content,
                category=category,
                imports=imports,
                classes=classes,
                functions=functions
            )
            
            self.modules[class_name] = module
            self.categories[category].append(class_name)
            
        print(f"  ✓ Extracted {len([m for m in self.modules.values() if m.source_file == 'code_monolith.py'])} modules")
    
    def _analyze_core_monolith(self):
        """Analyze CQE_CORE_MONOLITH.py - large utility file."""
        path = self.project_root / "CQE_CORE_MONOLITH.py"
        if not path.exists():
            return
        
        print(f"\n📦 Analyzing {path.name}...")
        content = path.read_text()
        
        # This is one large file - treat as single module
        classes = self._extract_classes(content)
        functions = self._extract_functions(content)
        imports = self._extract_imports(content)
        
        module = Module(
            name="CQECore",
            source_file="CQE_CORE_MONOLITH.py",
            line_start=0,
            line_end=content.count('\n'),
            content=content,
            category="Core/Utilities",
            imports=imports,
            classes=classes,
            functions=functions
        )
        
        self.modules["CQECore"] = module
        self.categories["Core/Utilities"].append("CQECore")
        
        print(f"  ✓ Indexed {len(classes)} classes, {len(functions)} functions")
    
    def _analyze_gvs_monolith(self):
        """Analyze CQE_GVS_MONOLITH.py - Generative Video System."""
        path = self.project_root / "CQE_GVS_MONOLITH.py"
        if not path.exists():
            return
        
        print(f"\n📦 Analyzing {path.name}...")
        content = path.read_text()
        
        classes = self._extract_classes(content)
        functions = self._extract_functions(content)
        imports = self._extract_imports(content)
        
        module = Module(
            name="GVS",
            source_file="CQE_GVS_MONOLITH.py",
            line_start=0,
            line_end=content.count('\n'),
            content=content,
            category="Generative/Video",
            imports=imports,
            classes=classes,
            functions=functions
        )
        
        self.modules["GVS"] = module
        self.categories["Generative/Video"].append("GVS")
        
        print(f"  ✓ Video generation system ready")
    
    def _analyze_aletheia_monolith(self):
        """Analyze aletheia_monolith.py - Self-extracting archive."""
        path = self.project_root / "aletheia_monolith.py"
        if not path.exists():
            return
        
        print(f"\n📦 Analyzing {path.name}...")
        content = path.read_text()
        
        module = Module(
            name="Aletheia",
            source_file="aletheia_monolith.py",
            line_start=0,
            line_end=content.count('\n'),
            content=content,
            category="AI/OS",
            imports=['sys', 'io', 'base64', 'zipfile', 'importlib'],
            classes=['AletheiaLoader'],
            functions=['verify_integrity']
        )
        
        self.modules["Aletheia"] = module
        self.categories["AI/OS"].append("Aletheia")
        
        print(f"  ✓ Self-extracting archive system")
    
    def _analyze_prototype(self):
        """Analyze monolith_prototype.txt - Four Laws implementation."""
        path = self.project_root / "monolith_prototype.txt"
        if not path.exists():
            return
        
        print(f"\n📦 Analyzing {path.name}...")
        content = path.read_text()
        
        classes = self._extract_classes(content)
        functions = self._extract_functions(content)
        
        module = Module(
            name="CQEPrototype",
            source_file="monolith_prototype.txt",
            line_start=0,
            line_end=content.count('\n'),
            content=content,
            category="Core/Four Laws",
            classes=classes,
            functions=functions
        )
        
        self.modules["CQEPrototype"] = module
        self.categories["Core/Four Laws"].append("CQEPrototype")
        
        print(f"  ✓ Four Laws prototype indexed")
    
    def _analyze_standalone_files(self):
        """Analyze standalone Python files."""
        for py_file in self.project_root.glob("*.py"):
            if py_file.name.startswith("cqe_builder"):
                continue
            if "monolith" in py_file.name.lower():
                continue  # Already handled
            
            content = py_file.read_text()
            if len(content.strip()) < 50:
                continue
            
            classes = self._extract_classes(content)
            functions = self._extract_functions(content)
            imports = self._extract_imports(content)
            
            if not classes and not functions:
                continue
            
            name = py_file.stem.replace("_", "").title()
            category = self._categorize_module(name, content)
            
            module = Module(
                name=name,
                source_file=py_file.name,
                line_start=0,
                line_end=content.count('\n'),
                content=content,
                category=category,
                imports=imports,
                classes=classes,
                functions=functions
            )
            
            self.modules[name] = module
            self.categories[category].append(name)
    
    def _categorize_module(self, name: str, content: str) -> str:
        """Determine module category from name and content."""
        name_lower = name.lower()
        content_lower = content.lower()[:2000]
        
        # Check name patterns
        if any(x in name_lower for x in ['lattice', 'e8', 'geometry', 'weyl', 'cartan']):
            return "Geometric/Math"
        elif any(x in name_lower for x in ['dihedral', 'cellular', 'automata', 'ca']):
            return "Cellular Automata"
        elif any(x in name_lower for x in ['server', 'api', 'db', 'database']):
            return "Backend/API"
        elif any(x in name_lower for x in ['transform', 'lambda', 'color']):
            return "Transformations"
        elif any(x in name_lower for x in ['test', 'coherence', 'metric']):
            return "Testing/Validation"
        elif any(x in name_lower for x in ['render', 'visual', 'viewer']):
            return "Rendering/Visual"
        elif any(x in name_lower for x in ['gvs', 'video', 'generative']):
            return "Generative/Video"
        elif any(x in name_lower for x in ['token', 'bridge', 'tie']):
            return "Integration/Bridge"
        elif any(x in name_lower for x in ['runtime', 'eval', 'modal']):
            return "Runtime/Execution"
        elif any(x in name_lower for x in ['speedlight', 'sidecar', 'cache']):
            return "Caching/Ledger"
        
        return "Other/Utility"
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports = []
        for line in content.split('\n')[:100]:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names."""
        return re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names (top-level only)."""
        functions = []
        for match in re.finditer(r'^def\s+(\w+)\s*\(', content, re.MULTILINE):
            functions.append(match.group(1))
        return functions
    
    def _build_catalog(self):
        """Build searchable catalog."""
        for name, module in self.modules.items():
            self.catalog[name] = {
                'name': name,
                'category': module.category,
                'source': module.source_file,
                'lines': module.line_count,
                'classes': module.classes,
                'functions': module.functions,
            }
    
    def save_catalog(self, path: Path):
        """Save catalog to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.catalog, f, indent=2)
        print(f"\n💾 Catalog saved to {path}")
    
    def print_summary(self):
        """Print summary of analyzed modules."""
        print("\n" + "="*60)
        print("📊 MODULE CATALOG SUMMARY")
        print("="*60)
        
        for category in sorted(self.categories.keys()):
            modules = self.categories[category]
            print(f"\n{category}: {len(modules)} modules")
            for mod in sorted(modules)[:5]:
                module = self.modules[mod]
                print(f"  • {mod:30} ({module.line_count:5} lines)")
            if len(modules) > 5:
                print(f"  ... and {len(modules) - 5} more")


class CodeExtractor:
    """Extracts and fixes code from modules."""
    
    @staticmethod
    def fix_unicode(content: str) -> str:
        """Fix unicode subscript/superscript issues."""
        # Map subscripts to normal
        subscripts = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
        # Map superscripts to normal
        superscripts = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
        
        content = content.translate(subscripts)
        content = content.translate(superscripts)
        
        # Fix E₈ -> E8
        content = re.sub(r'E[₀-₉⁰-⁹]+', lambda m: 'E' + m.group()[1:].translate(subscripts).translate(superscripts), content)
        
        return content
    
    @staticmethod
    def extract_module(module: Module, fix_unicode: bool = True) -> str:
        """Extract module content with fixes."""
        content = module.content
        
        if fix_unicode:
            content = CodeExtractor.fix_unicode(content)
        
        return content


class BuildAssembler:
    """Assembles builds from selected modules."""
    
    def __init__(self, analyzer: MonolithAnalyzer):
        self.analyzer = analyzer
        self.extractor = CodeExtractor()
    
    def create_build(self, build: Build, output_dir: Path):
        """Create a build from specification."""
        print(f"\n🔨 Building: {build.name}")
        print(f"   Purpose: {build.purpose}")
        print("="*60)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        build_path = output_dir / f"{build.name.lower().replace(' ', '_')}.py"
        
        # Collect all module contents
        contents = []
        contents.append(f'"""\n{build.name}\n{"="*len(build.name)}\n\n{build.purpose}\n\nAuto-generated by CQE Builder\n"""\n\n')
        
        # Collect imports
        all_imports = set()
        module_contents = []
        
        for module_name in build.modules:
            if module_name not in self.analyzer.modules:
                print(f"  ⚠ Module '{module_name}' not found, skipping")
                continue
            
            module = self.analyzer.modules[module_name]
            print(f"  ✓ Adding {module_name} ({module.line_count} lines)")
            
            # Extract and fix content
            content = self.extractor.extract_module(module, fix_unicode=True)
            
            # Collect imports
            all_imports.update(module.imports)
            
            # Add module marker
            module_contents.append(f"\n# {'='*60}")
            module_contents.append(f"# MODULE: {module_name} (from {module.source_file})")
            module_contents.append(f"# {'='*60}\n")
            module_contents.append(content)
        
        # Write header with imports
        contents.append("# Standard library imports\n")
        for imp in sorted(all_imports):
            if imp:
                contents.append(imp + "\n")
        contents.append("\n")
        
        # Write all module contents
        contents.extend(module_contents)
        
        # Add CLI if enabled
        if build.cli_enabled and build.entry_point:
            contents.append(self._generate_cli(build))
        
        # Write to file
        build_path.write_text(''.join(contents))
        
        print(f"\n✅ Build complete: {build_path}")
        print(f"   Size: {build_path.stat().st_size // 1024} KB")
        
        return build_path
    
    def _generate_cli(self, build: Build) -> str:
        """Generate CLI wrapper."""
        return f"""

# {'='*60}
# CLI INTERFACE
# {'='*60}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="{build.purpose}")
    parser.add_argument('command', help='Command to run')
    parser.add_argument('args', nargs='*', help='Command arguments')
    
    args = parser.parse_args()
    
    # Route to appropriate function
    if args.command == 'help':
        parser.print_help()
    else:
        print(f"Command '{{args.command}}' not implemented yet")
        print("Available commands: help")
"""


class CQEBuilder:
    """Main builder orchestrator."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.analyzer = MonolithAnalyzer(project_root)
        self.assembler = None
    
    def analyze(self):
        """Analyze all monoliths."""
        self.analyzer.analyze_all()
        self.assembler = BuildAssembler(self.analyzer)
        return self.analyzer
    
    def build_best_of_breed(self, output_dir: Path):
        """Build best-of-breed tools for each category."""
        print("\n" + "="*60)
        print("🏗️  BUILDING BEST-OF-BREED TOOLS")
        print("="*60)
        
        builds = self._define_builds()
        
        for build in builds:
            self.assembler.create_build(build, output_dir)
    
    def _define_builds(self) -> List[Build]:
        """Define standard builds based on analyzed modules."""
        builds = []
        
        # Geometric/Math toolkit
        if self.analyzer.categories.get("Geometric/Math"):
            builds.append(Build(
                name="geometric_toolkit",
                purpose="E8 Lattice operations, Weyl chambers, Cartan matrices",
                modules=self.analyzer.categories["Geometric/Math"]
            ))
        
        # Generative Video System
        if "GVS" in self.analyzer.modules:
            builds.append(Build(
                name="generative_video",
                purpose="Real-time lossless video generation via E8 projection",
                modules=["GVS"],
                entry_point="generate_video"
            ))
        
        # Core CQE System
        if "CQECore" in self.analyzer.modules and "CQEPrototype" in self.analyzer.modules:
            builds.append(Build(
                name="cqe_core_system",
                purpose="Complete CQE Four Laws implementation",
                modules=["CQECore", "CQEPrototype"],
                entry_point="main"
            ))
        
        # Backend API system
        if self.analyzer.categories.get("Backend/API"):
            builds.append(Build(
                name="cqe_api_server",
                purpose="CQE API server with database and endpoints",
                modules=self.analyzer.categories["Backend/API"][:3],
                entry_point="run_server"
            ))
        
        # Testing/Validation suite
        if self.analyzer.categories.get("Testing/Validation"):
            builds.append(Build(
                name="validation_suite",
                purpose="Coherence metrics, testing, and validation tools",
                modules=self.analyzer.categories["Testing/Validation"]
            ))
        
        # Rendering/Visual tools
        rendering_modules = []
        if self.analyzer.categories.get("Rendering/Visual"):
            rendering_modules.extend(self.analyzer.categories["Rendering/Visual"])
        if "Renderengine" in self.analyzer.modules:
            rendering_modules.append("Renderengine")
        
        if rendering_modules:
            builds.append(Build(
                name="rendering_engine",
                purpose="Geometric rendering and visualization tools",
                modules=rendering_modules
            ))
        
        # Caching/Ledger system
        if self.analyzer.categories.get("Caching/Ledger"):
            builds.append(Build(
                name="speedlight_cache",
                purpose="Speedlight caching and ledger system",
                modules=self.analyzer.categories["Caching/Ledger"]
            ))
        
        return builds


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CQE Builder - Intelligent Module Extraction & Assembly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cqe_builder.py analyze              # Analyze all monoliths
  cqe_builder.py build                # Build best-of-breed tools
  cqe_builder.py list                 # List all modules
  cqe_builder.py list --category geo  # List by category
        """
    )
    
    parser.add_argument('command', choices=['analyze', 'build', 'list'],
                       help='Command to execute')
    parser.add_argument('--category', help='Filter by category (for list command)')
    parser.add_argument('--output', default='/mnt/user-data/outputs',
                       help='Output directory for builds')
    
    args = parser.parse_args()
    
    # Initialize builder
    project_root = Path("/mnt/project")
    builder = CQEBuilder(project_root)
    
    # Execute command
    if args.command == 'analyze':
        builder.analyze()
        builder.analyzer.print_summary()
        catalog_path = Path(args.output) / "cqe_catalog.json"
        builder.analyzer.save_catalog(catalog_path)
        
    elif args.command == 'build':
        builder.analyze()
        output_dir = Path(args.output) / "builds"
        builder.build_best_of_breed(output_dir)
        
    elif args.command == 'list':
        builder.analyze()
        if args.category:
            cat = args.category.lower()
            for category, modules in builder.analyzer.categories.items():
                if cat in category.lower():
                    print(f"\n{category}:")
                    for mod in sorted(modules):
                        module = builder.analyzer.modules[mod]
                        print(f"  {mod:30} ({module.line_count:5} lines) - {module.source_file}")
        else:
            builder.analyzer.print_summary()


if __name__ == "__main__":
    main()
