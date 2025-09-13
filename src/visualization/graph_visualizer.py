"""
Graph Visualizer
Handles graph structure visualization
"""

def save_graph_visualization(graph, filename="src/visualization/graph_visualization.png"):
    """Save graph visualization as PNG file"""
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(png_data)
        print(f"✅ Graph visualization saved as '{filename}'")
        return True
    except Exception as e:
        print(f"❌ Failed to save graph visualization: {e}")
        return False


if __name__ == "__main__":
    """Standalone script to save the LangGraph workflow visualization"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from services.graph_service import graph
    
    print("🔄 Generating graph visualization...")
    
    try:
        # Save the graph visualization
        success = save_graph_visualization(graph, "src/visualization/graph_visualization.png")
        
        if success:
            print("✅ Graph visualization saved successfully!")
            print("📁 File location: graph_visualization.png")
        else:
            print("❌ Failed to save graph visualization")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error generating graph visualization: {e}")
        sys.exit(1)
