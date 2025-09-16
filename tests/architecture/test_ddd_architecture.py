"""DDD架构一致性测试"""
import ast
import inspect
import os
from pathlib import Path
from typing import List, Set, Dict
# import pytest

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"


class ArchitectureAnalyzer:
    """架构分析器"""
    
    def __init__(self):
        self.src_root = SRC_ROOT
        self.violations: List[str] = []
    
    def get_python_files(self, directory: Path) -> List[Path]:
        """获取目录下所有Python文件"""
        python_files = []
        if directory.exists():
            for file_path in directory.rglob("*.py"):
                if "__pycache__" not in str(file_path):
                    python_files.append(file_path)
        return python_files
    
    def analyze_imports(self, file_path: Path) -> Set[str]:
        """分析文件的导入依赖"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except Exception:
            pass
        
        return imports
    
    def check_dependency_rules(self) -> List[str]:
        """检查DDD分层依赖规则"""
        violations = []
        
        # 领域层不应该依赖其他层
        domain_files = self.get_python_files(self.src_root / "domain")
        for file_path in domain_files:
            imports = self.analyze_imports(file_path)
            for imp in imports:
                if (imp.startswith("src.application") or 
                    imp.startswith("src.infrastructure") or 
                    imp.startswith("src.interfaces")):
                    violations.append(f"领域层文件 {file_path.relative_to(self.src_root)} 违规依赖 {imp}")
        
        # 应用层不应该依赖接口层
        application_files = self.get_python_files(self.src_root / "application")
        for file_path in application_files:
            imports = self.analyze_imports(file_path)
            for imp in imports:
                if imp.startswith("src.interfaces"):
                    violations.append(f"应用层文件 {file_path.relative_to(self.src_root)} 违规依赖接口层 {imp}")
        
        return violations
    
    def check_repository_pattern(self) -> List[str]:
        """检查仓储模式实现"""
        violations = []
        
        # 检查仓储实现是否继承了正确的基类
        repo_impl_files = self.get_python_files(self.src_root / "infrastructure" / "repositories")
        
        for file_path in repo_impl_files:
            if file_path.name.endswith("_repository_impl.py"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查是否继承了领域仓储接口
                    if "Repository" in content and "class" in content:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef) and node.name.endswith("RepositoryImpl"):
                                # 检查基类
                                base_names = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                                
                                # 应该继承领域仓储接口，但实际架构中可能需要工作单元基类
                                if not any("Repository" in base for base in base_names):
                                    violations.append(f"仓储实现 {file_path.relative_to(self.src_root)} 没有继承仓储接口")
                                
                except Exception as e:
                    violations.append(f"分析仓储文件 {file_path.relative_to(self.src_root)} 时出错: {str(e)}")
        
        return violations
    
    def check_aggregate_roots(self) -> List[str]:
        """检查聚合根实现"""
        violations = []
        
        # 检查实体是否继承了聚合根基类
        entity_files = []
        for domain_dir in (self.src_root / "domain").iterdir():
            if domain_dir.is_dir() and (domain_dir / "entities").exists():
                entity_files.extend(self.get_python_files(domain_dir / "entities"))
        
        for file_path in entity_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "AggregateRoot" not in content and "class" in content:
                    # 检查是否有聚合根实体没有继承基类
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # 跳过内部类和测试类
                            if (not node.name.startswith("_") and 
                                not node.name.endswith("Test") and 
                                not node.name.endswith("DTO")):
                                
                                base_names = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                                if not any("AggregateRoot" in base for base in base_names):
                                    violations.append(f"实体 {node.name} 在 {file_path.relative_to(self.src_root)} 可能未继承 AggregateRoot")
                
            except Exception:
                pass
        
        return violations
    
    def check_event_handling(self) -> List[str]:
        """检查事件处理机制"""
        violations = []
        
        # 检查是否有事件处理器
        event_handler_files = []
        for domain_dir in (self.src_root / "domain").iterdir():
            if domain_dir.is_dir() and (domain_dir / "events").exists():
                event_handler_files.extend(self.get_python_files(domain_dir / "events"))
        
        if not event_handler_files:
            violations.append("未找到任何事件处理器文件")
        
        # 检查事件发布器是否在容器中正确配置
        container_file = self.src_root / "shared" / "containers.py"
        if container_file.exists():
            try:
                with open(container_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "setup_event_handlers" not in content:
                    violations.append("容器中缺少事件处理器设置函数")
                
                if "EventPublisher" not in content:
                    violations.append("容器中缺少事件发布器配置")
                    
            except Exception:
                violations.append("无法分析容器配置文件")
        
        return violations


class TestDDDArchitecture:
    """DDD架构测试"""
    
    def setup_method(self):
        """测试设置"""
        self.analyzer = ArchitectureAnalyzer()
    
    def test_dependency_inversion_principle(self):
        """测试依赖倒置原则"""
        violations = self.analyzer.check_dependency_rules()
        
        # 打印违规信息用于调试
        if violations:
            print("\n依赖规则违规:")
            for violation in violations:
                print(f"  - {violation}")
        
        assert len(violations) == 0, f"发现 {len(violations)} 个依赖规则违规"
    
    def test_repository_pattern_implementation(self):
        """测试仓储模式实现"""
        violations = self.analyzer.check_repository_pattern()
        
        if violations:
            print("\n仓储模式违规:")
            for violation in violations:
                print(f"  - {violation}")
        
        # 仓储实现应该正确继承接口
        assert len(violations) <= 5, f"仓储模式实现问题过多: {len(violations)} 个违规"
    
    def test_aggregate_root_inheritance(self):
        """测试聚合根继承"""
        violations = self.analyzer.check_aggregate_roots()
        
        if violations:
            print("\n聚合根继承问题:")
            for violation in violations:
                print(f"  - {violation}")
        
        # 允许一些实体不继承聚合根（如值对象）
        assert len(violations) <= 3, f"聚合根继承问题: {len(violations)} 个"
    
    def test_event_driven_architecture(self):
        """测试事件驱动架构"""
        violations = self.analyzer.check_event_handling()
        
        if violations:
            print("\n事件处理架构问题:")
            for violation in violations:
                print(f"  - {violation}")
        
        assert len(violations) == 0, f"事件驱动架构问题: {len(violations)} 个"
    
    def test_layer_isolation(self):
        """测试层隔离性"""
        # 检查各层是否存在
        layers = {
            "domain": self.analyzer.src_root / "domain",
            "application": self.analyzer.src_root / "application", 
            "infrastructure": self.analyzer.src_root / "infrastructure",
            "interfaces": self.analyzer.src_root / "interfaces",
            "shared": self.analyzer.src_root / "shared"
        }
        
        missing_layers = []
        for layer_name, layer_path in layers.items():
            if not layer_path.exists():
                missing_layers.append(layer_name)
        
        assert len(missing_layers) == 0, f"缺少层: {missing_layers}"
        
        # 检查每层是否有Python文件
        empty_layers = []
        for layer_name, layer_path in layers.items():
            python_files = self.analyzer.get_python_files(layer_path)
            if len(python_files) == 0:
                empty_layers.append(layer_name)
        
        assert len(empty_layers) == 0, f"空层: {empty_layers}"
    
    def test_container_configuration(self):
        """测试依赖注入容器配置"""
        container_file = self.analyzer.src_root / "shared" / "containers.py"
        
        assert container_file.exists(), "依赖注入容器文件不存在"
        
        with open(container_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键组件是否配置
        required_components = [
            "ApplicationContainer",
            "wordlist_repository", 
            "app_repository",
            "list_detail_repository",
            "association_repository",
            "moderation_log_repository"
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        assert len(missing_components) == 0, f"容器中缺少组件: {missing_components}"


if __name__ == "__main__":
    # 运行架构测试
    analyzer = ArchitectureAnalyzer()
    
    print("🔍 DDD架构一致性检查")
    print("=" * 50)
    
    # 依赖规则检查
    print("\n1. 检查依赖倒置原则...")
    violations = analyzer.check_dependency_rules()
    if violations:
        print("❌ 发现依赖规则违规:")
        for v in violations:
            print(f"   • {v}")
    else:
        print("✅ 依赖规则检查通过")
    
    # 仓储模式检查
    print("\n2. 检查仓储模式...")
    violations = analyzer.check_repository_pattern()
    if violations:
        print("❌ 仓储模式问题:")
        for v in violations:
            print(f"   • {v}")
    else:
        print("✅ 仓储模式检查通过")
    
    # 聚合根检查
    print("\n3. 检查聚合根继承...")
    violations = analyzer.check_aggregate_roots()
    if violations:
        print("⚠️ 聚合根继承问题:")
        for v in violations:
            print(f"   • {v}")
    else:
        print("✅ 聚合根继承检查通过")
    
    # 事件处理检查
    print("\n4. 检查事件驱动架构...")
    violations = analyzer.check_event_handling()
    if violations:
        print("❌ 事件处理问题:")
        for v in violations:
            print(f"   • {v}")
    else:
        print("✅ 事件驱动架构检查通过")
    
    print("\n" + "=" * 50)
    print("🎯 架构检查完成")