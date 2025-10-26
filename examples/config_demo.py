"""
Configuration System Demo

Demonstrates the three operational modes and configuration loader.

This example shows:
1. Loading different mode configurations
2. Inspecting mode capabilities
3. Checking enabled Skills/Agents
4. Accessing performance targets
"""

from core import ConfigLoader, load_config, get_active_mode


def print_separator():
    """Print visual separator"""
    print("\n" + "=" * 80 + "\n")


def demo_hybrid_mode():
    """Demonstrate hybrid mode configuration"""
    print("🔀 HYBRID MODE (Default)")
    print("-" * 80)

    loader = ConfigLoader()
    config = loader.load_mode("hybrid")

    # Mode info
    mode_info = config["mode"]
    print(f"Name: {mode_info['name']}")
    print(f"Description: {mode_info['description']}")
    print(f"Default: {mode_info['default']}")

    # Routing configuration
    print(f"\nRouting Enabled: {loader.is_routing_enabled()}")
    routing = config["routing"]
    print(f"Router Class: {routing['router_class']}")
    print(f"Fallback Target: {routing['fallback']['default_target']}")

    # Skills configuration
    print(f"\nSkills Enabled: {loader.are_skills_enabled()}")
    skills = loader.get_enabled_skills()
    print(f"Skill Categories: {list(skills.keys())}")
    print(f"Total Skills: {sum(len(s) for s in skills.values())}")

    # Agents configuration
    print(f"\nAgents Enabled: {loader.are_agents_enabled()}")
    agents = loader.get_enabled_agents()
    print(f"Specialized Agents: {len(agents)}")
    print(f"Orchestrator Enabled: {loader.is_orchestrator_enabled()}")

    # Performance targets
    perf = loader.get_performance_targets()
    print(f"\nToken Reduction Target: {perf['token_reduction']['target']*100}%")
    distribution = perf["distribution"]
    print(f"Expected Distribution:")
    print(f"  - Skills: {distribution['skills']*100}%")
    print(f"  - Agents: {distribution['agents']*100}%")
    print(f"  - Orchestrator: {distribution['orchestrator']*100}%")


def demo_skills_only_mode():
    """Demonstrate skills-only mode configuration"""
    print("⚡ SKILLS-ONLY MODE (Maximum Efficiency)")
    print("-" * 80)

    loader = ConfigLoader()
    config = loader.load_mode("skills_only")

    # Mode info
    mode_info = config["mode"]
    print(f"Name: {mode_info['name']}")
    print(f"Description: {mode_info['description']}")

    # Key settings
    print(f"\nRouting Enabled: {config['routing']['enabled']}")
    print(f"Force Target: {config['routing']['force_target']}")

    print(f"\nSkills Enabled: {config['skills']['enabled']}")
    print(f"Agents Enabled: {config['agents']['enabled']}")

    # Skills details
    skills_config = config["skills"]
    skill_categories = [
        "data_extraction",
        "technical_analysis",
        "sentiment_analysis",
    ]
    total_skills = sum(len(skills_config[cat]) for cat in skill_categories)
    print(f"\nTotal Skills Available: {total_skills}")

    # Performance
    perf = config["performance"]
    print(f"\nToken Reduction Target: {perf['token_reduction']['target']*100}%")
    print(f"Query Distribution: {perf['distribution']['skills']*100}% Skills")

    # Limitations
    print(f"\nLimitations:")
    for limitation in perf["limitations"]:
        print(f"  - {limitation}")


def demo_agents_only_mode():
    """Demonstrate agents-only mode configuration"""
    print("🧠 AGENTS-ONLY MODE (Maximum Reasoning)")
    print("-" * 80)

    loader = ConfigLoader()
    config = loader.load_mode("agents_only")

    # Mode info
    mode_info = config["mode"]
    print(f"Name: {mode_info['name']}")
    print(f"Description: {mode_info['description']}")

    # Key settings
    print(f"\nRouting Enabled: {config['routing']['enabled']}")
    print(f"Force Target: {config['routing']['force_target']}")

    print(f"\nSkills Enabled: {config['skills']['enabled']}")
    print(f"Agents Enabled: {config['agents']['enabled']}")

    # Agents details
    agents_config = config["agents"]
    specialized = agents_config["specialized"]
    print(f"\nSpecialized Agents: {len(specialized)}")
    for agent in specialized:
        print(f"  - {agent}")

    orchestrator = agents_config["orchestrator"]
    print(f"\nOrchestrator Enabled: {orchestrator['enabled']}")
    print(f"Orchestrator Agent: {orchestrator['agent']}")
    print(f"Auto-Invoke: {orchestrator['auto_invoke']}")

    # Capabilities
    capabilities = agents_config["capabilities"]
    print(f"\nCapabilities:")
    for cap, enabled in capabilities.items():
        print(f"  - {cap.replace('_', ' ').title()}: {enabled}")

    # Performance
    perf = config["performance"]
    print(f"\nToken Reduction Target: {perf['token_reduction']['target']*100}%")
    print(f"Agent Overhead: {perf['token_reduction']['agent_overhead']*100}%")

    # Benefits
    print(f"\nBenefits:")
    for benefit in perf["benefits"]:
        print(f"  ✓ {benefit}")

    # Trade-offs
    print(f"\nTrade-offs:")
    for tradeoff in perf["tradeoffs"]:
        print(f"  ⚠ {tradeoff}")


def demo_mode_switching():
    """Demonstrate switching between modes"""
    print("🔄 MODE SWITCHING DEMO")
    print("-" * 80)

    loader = ConfigLoader()

    # Start with hybrid (default)
    loader.set_active_mode("hybrid")
    print(f"Active Mode: {loader.get_active_mode_name()}")
    print(f"Routing Enabled: {loader.is_routing_enabled()}")
    print(f"Skills Enabled: {loader.are_skills_enabled()}")
    print(f"Agents Enabled: {loader.are_agents_enabled()}")

    print("\n→ Switching to skills_only...")
    loader.set_active_mode("skills_only")
    print(f"Active Mode: {loader.get_active_mode_name()}")
    print(f"Routing Enabled: {loader.is_routing_enabled()}")
    print(f"Skills Enabled: {loader.are_skills_enabled()}")
    print(f"Agents Enabled: {loader.are_agents_enabled()}")

    print("\n→ Switching to agents_only...")
    loader.set_active_mode("agents_only")
    print(f"Active Mode: {loader.get_active_mode_name()}")
    print(f"Routing Enabled: {loader.is_routing_enabled()}")
    print(f"Skills Enabled: {loader.are_skills_enabled()}")
    print(f"Agents Enabled: {loader.are_agents_enabled()}")


def demo_mcp_servers():
    """Demonstrate MCP server requirements per mode"""
    print("🔌 MCP SERVER REQUIREMENTS BY MODE")
    print("-" * 80)

    loader = ConfigLoader()
    modes = ["hybrid", "skills_only", "agents_only"]

    for mode in modes:
        config = loader.load_mode(mode)
        servers = config["mcp"]["servers"]

        print(f"\n{mode.upper()}:")
        required_servers = [s for s in servers if s["required"]]
        optional_servers = [s for s in servers if not s["required"]]

        print(f"  Required ({len(required_servers)}):")
        for server in required_servers:
            usage = ", ".join(server["usage"])
            print(f"    - {server['name']} (used by: {usage})")

        if optional_servers:
            print(f"  Optional ({len(optional_servers)}):")
            for server in optional_servers:
                usage = ", ".join(server["usage"]) if server["usage"] else "none"
                print(f"    - {server['name']} (used by: {usage})")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "CRYPTO-SKILLS-MCP CONFIGURATION SYSTEM" + " " * 19 + "║")
    print("╚" + "═" * 78 + "╝")

    print_separator()
    demo_hybrid_mode()

    print_separator()
    demo_skills_only_mode()

    print_separator()
    demo_agents_only_mode()

    print_separator()
    demo_mode_switching()

    print_separator()
    demo_mcp_servers()

    print_separator()
    print("✅ Configuration system demo complete!")
    print("\nTo use in production:")
    print('  export CRYPTO_SKILLS_MODE="hybrid"  # or skills_only, agents_only')
    print("  from core import ConfigLoader")
    print("  loader = ConfigLoader()")
    print("  config = loader.get_active_config()")
    print()
