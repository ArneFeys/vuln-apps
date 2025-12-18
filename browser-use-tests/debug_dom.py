"""
Debug script to inspect indexed DOM elements on a webpage.
"""

import asyncio
from browser_use import BrowserSession
from browser_use.dom.service import DomService
from browser_use.dom.serializer.clickable_elements import ClickableElementDetector


async def debug_dom_state(url: str = "https://app.knowlex.be"):
    """Navigate to a URL and dump the DOM state to see what elements are indexed."""
    
    print(f"\n{'='*60}")
    print(f"Debugging DOM state for: {url}")
    print(f"{'='*60}\n")
    
    session = BrowserSession(
        headless=False,
        paint_order_filtering=False,  # Fix for knowlex - elements were incorrectly filtered
    )
    
    try:
        # Start browser session
        print("Starting browser session...")
        await session.start()
        
        # Navigate to the page
        print(f"Navigating to {url}...")
        await session.navigate_to(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        await asyncio.sleep(4)
        
        print("Getting browser state...")
        state = await session.get_browser_state_summary()
        
        print(f"\n{'='*60}")
        print("INDEXED ELEMENTS (elements the agent can interact with)")
        print(f"{'='*60}")
        print(f"Total indexed elements: {len(state.dom_state.selector_map)}\n")
        
        for idx, elem in state.dom_state.selector_map.items():
            attrs = elem.attributes or {}
            text = elem.get_all_children_text()[:80].replace('\n', ' ').strip()
            
            # Build attribute summary
            attr_parts = []
            if attrs.get('id'):
                attr_parts.append(f"id={attrs['id']}")
            if attrs.get('class'):
                attr_parts.append(f"class={attrs['class'][:40]}")
            if attrs.get('type'):
                attr_parts.append(f"type={attrs['type']}")
            if attrs.get('name'):
                attr_parts.append(f"name={attrs['name']}")
            if attrs.get('role'):
                attr_parts.append(f"role={attrs['role']}")
            if attrs.get('href'):
                attr_parts.append(f"href={attrs['href'][:50]}")
            
            attr_str = ' '.join(attr_parts) if attr_parts else ''
            
            print(f"[{idx}] <{elem.tag_name}> {attr_str}")
            if text:
                print(f"      Text: \"{text}\"")
        
        print(f"\n{'='*60}")
        print("LLM DOM VIEW (what the agent sees)")
        print(f"{'='*60}\n")
        
        llm_view = state.dom_state.llm_representation()
        print(llm_view)
        
        print(f"\n{'='*60}")
        print("INTERACTIVE ELEMENT STATISTICS")
        print(f"{'='*60}")
        
        # Count by tag type
        tag_counts = {}
        for elem in state.dom_state.selector_map.values():
            tag = elem.tag_name.lower()
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print("\nBy tag type:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"  {tag}: {count}")

        # Also get the raw DOM tree to see what elements exist but aren't indexed
        print(f"\n{'='*60}")
        print("ANALYZING WHY ELEMENTS AREN'T INDEXED")
        print(f"{'='*60}")
        
        dom_service = DomService(session)
        dom_tree, timing = await dom_service.get_dom_tree(session.agent_focus_target_id)
        
        # Find all potentially interactive elements
        potential_interactive = []
        
        def find_elements(node, depth=0):
            """Recursively find potentially interactive elements."""
            if node is None:
                return
            
            tag = node.tag_name.lower() if node.tag_name else ''
            attrs = node.attributes or {}
            
            # Check for form elements, buttons, links
            if tag in ['input', 'button', 'a', 'select', 'textarea']:
                is_interactive = ClickableElementDetector.is_interactive(node)
                potential_interactive.append({
                    'tag': tag,
                    'id': attrs.get('id', ''),
                    'class': attrs.get('class', '')[:50],
                    'type': attrs.get('type', ''),
                    'href': attrs.get('href', '')[:50] if tag == 'a' else '',
                    'text': node.get_all_children_text()[:50].replace('\n', ' ').strip(),
                    'visible': node.is_visible,
                    'has_snapshot': node.snapshot_node is not None,
                    'backend_node_id': node.backend_node_id,
                    'indexed': node.backend_node_id in state.dom_state.selector_map,
                    'is_interactive_check': is_interactive,
                })
            
            # Also check for elements with click handlers or button roles
            if attrs.get('onclick') or attrs.get('role') == 'button' or 'btn' in attrs.get('class', '').lower():
                if tag not in ['input', 'button', 'a', 'select', 'textarea']:
                    potential_interactive.append({
                        'tag': tag,
                        'id': attrs.get('id', ''),
                        'class': attrs.get('class', '')[:50],
                        'type': attrs.get('type', ''),
                        'onclick': 'yes' if attrs.get('onclick') else '',
                        'role': attrs.get('role', ''),
                        'text': node.get_all_children_text()[:50].replace('\n', ' ').strip(),
                        'visible': node.is_visible,
                        'has_snapshot': node.snapshot_node is not None,
                        'backend_node_id': node.backend_node_id,
                        'indexed': node.backend_node_id in state.dom_state.selector_map,
                    })
            
            # Debug: Check why elements might not be indexed
            if tag in ['input', 'button', 'a'] and not (node.backend_node_id in state.dom_state.selector_map):
                # Check for AX properties
                ax_info = None
                if node.ax_node:
                    ax_info = {
                        'role': node.ax_node.role,
                        'name': node.ax_node.name,
                        'ignored': node.ax_node.ignored,
                        'properties': [(p.name, p.value) for p in (node.ax_node.properties or [])],
                    }
                
                # Check computed styles
                styles = None
                if node.snapshot_node and node.snapshot_node.computed_styles:
                    styles = {
                        'display': node.snapshot_node.computed_styles.get('display'),
                        'visibility': node.snapshot_node.computed_styles.get('visibility'),
                        'opacity': node.snapshot_node.computed_styles.get('opacity'),
                    }
                
                potential_interactive[-1]['ax_info'] = ax_info
                potential_interactive[-1]['styles'] = styles
                potential_interactive[-1]['bounds'] = node.snapshot_node.bounds if node.snapshot_node else None
                
                # Get parent chain visibility
                parent_chain = []
                parent = node.parent_node
                while parent and len(parent_chain) < 5:
                    p_visible = parent.is_visible
                    p_tag = parent.tag_name.lower() if parent.tag_name else 'unknown'
                    p_has_snapshot = parent.snapshot_node is not None
                    parent_chain.append(f"{p_tag}(vis={p_visible},snap={p_has_snapshot})")
                    parent = parent.parent_node
                potential_interactive[-1]['parent_chain'] = ' > '.join(parent_chain) if parent_chain else 'no parents'
            
            # Recurse into children
            for child in node.children or []:
                find_elements(child, depth + 1)
            
            # Also check shadow roots and content documents
            if node.shadow_roots:
                for shadow_root in node.shadow_roots:
                    find_elements(shadow_root, depth + 1)
            if node.content_document:
                find_elements(node.content_document, depth + 1)
        
        find_elements(dom_tree)
        
        print(f"\nFound {len(potential_interactive)} potentially interactive elements:\n")
        
        for elem in potential_interactive:
            status = "✅ INDEXED" if elem['indexed'] else "❌ NOT INDEXED"
            visible = "visible" if elem['visible'] else "hidden"
            
            is_interactive_str = "✅ IS_INTERACTIVE" if elem.get('is_interactive_check') else "❌ NOT_INTERACTIVE"
            print(f"{status} <{elem['tag']}> [{elem['backend_node_id']}] {is_interactive_str}")
            if elem.get('id'):
                print(f"   id: {elem['id']}")
            if elem.get('class'):
                print(f"   class: {elem['class']}")
            if elem.get('type'):
                print(f"   type: {elem['type']}")
            if elem.get('text'):
                print(f"   text: \"{elem['text']}\"")
            print(f"   {visible}, has_snapshot={elem['has_snapshot']}")
            
            # Print extra debug info for non-indexed elements
            if not elem['indexed']:
                if elem.get('ax_info'):
                    ax = elem['ax_info']
                    print(f"   AX: role={ax.get('role')}, name={ax.get('name')}, ignored={ax.get('ignored')}")
                    if ax.get('properties'):
                        props = [f"{p[0]}={p[1]}" for p in ax['properties'][:5]]
                        print(f"   AX props: {', '.join(props)}")
                if elem.get('styles'):
                    styles = elem['styles']
                    print(f"   Styles: display={styles.get('display')}, visibility={styles.get('visibility')}, opacity={styles.get('opacity')}")
                if elem.get('bounds'):
                    b = elem['bounds']
                    print(f"   Bounds: x={b.x:.0f}, y={b.y:.0f}, w={b.width:.0f}, h={b.height:.0f}")
                if elem.get('parent_chain'):
                    print(f"   Parent chain: {elem['parent_chain']}")
            print()
        
        print(f"\n{'='*60}")
        print("Waiting 5 seconds before closing browser...")
        await asyncio.sleep(5)
        
    finally:
        # Clean up
        await session.stop()


if __name__ == "__main__":
    asyncio.run(debug_dom_state())

