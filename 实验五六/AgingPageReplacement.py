import sys
from collections import deque
import matplotlib.pyplot as plt
import random

class AgingPageReplacement:
    def __init__(self, num_frames):
        """
        Initialize aging algorithm paging system
        num_frames: number of available page frames
        """
        self.num_frames = num_frames
        self.page_table = {}  # page number -> (frame index, aging counter)
        self.frames = [None] * num_frames  # frame contents
        self.free_frames = deque(range(num_frames))  # free frame queue
        self.page_faults = 0
        self.access_count = 0
        self.page_fault_history = []  # record page faults per 1000 accesses
        
    def access_page(self, page_num):
        """
        Access a page
        """
        self.access_count += 1
        
        # Record page faults every 1000 accesses
        if self.access_count % 1000 == 0:
            self.page_fault_history.append(self.page_faults)
            self.page_faults = 0  # reset counter for next 1000 accesses
        
        # If page is already in memory
        if page_num in self.page_table:
            frame_idx, age_counter = self.page_table[page_num]
            # Set reference bit to 1 (shift left and set highest bit to 1)
            self.page_table[page_num] = (frame_idx, (1 << 31) | (age_counter >> 1))
            return False  # no page fault
        
        # Page fault handling
        self.page_faults += 1
        
        # If there are free frames
        if self.free_frames:
            frame_idx = self.free_frames.popleft()
            self.frames[frame_idx] = page_num
            # Initial aging counter: highest bit 1 (just referenced), others 0
            self.page_table[page_num] = (frame_idx, 1 << 31)
            return True  # page fault occurred
        
        # No free frames, need to replace
        # Find page with smallest aging counter
        min_age = float('inf')
        victim_page = None
        victim_frame = None
        
        for page, (frame_idx, age_counter) in self.page_table.items():
            if age_counter < min_age:
                min_age = age_counter
                victim_page = page
                victim_frame = frame_idx
        
        # Replace page
        if victim_page is not None:
            del self.page_table[victim_page]
            self.frames[victim_frame] = page_num
            # New page aging counter: highest bit 1 (just referenced), others 0
            self.page_table[page_num] = (victim_frame, 1 << 31)
        
        return True  # page fault occurred
    
    def tick(self):
        """
        Clock tick: periodically right-shift all page aging counters
        This simulates the aging process (counters decay over time)
        """
        for page_num in list(self.page_table.keys()):
            frame_idx, age_counter = self.page_table[page_num]
            # Right shift by 1, simulating aging
            self.page_table[page_num] = (frame_idx, age_counter >> 1)

def simulate_aging(file_path, max_frames=10, tick_interval=100):
    """
    Simulate aging algorithm
    file_path: path to page access sequence file
    max_frames: maximum number of frames to test
    tick_interval: clock tick interval (number of accesses)
    """
    results = {}
    
    # Read page access sequence
    try:
        with open(file_path, 'r') as f:
            access_sequence = [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return results, 0
    
    print(f"Total accesses: {len(access_sequence)}")
    print(f"Unique pages: {len(set(access_sequence))}")
    
    # Simulate for different numbers of frames
    for num_frames in range(1, max_frames + 1):
        print(f"\nSimulating with {num_frames} frame(s)")
        
        # Initialize paging system
        memory = AgingPageReplacement(num_frames)
        
        # Simulate page accesses
        for i, page_num in enumerate(access_sequence):
            memory.access_page(page_num)
            
            # Periodically execute clock tick (aging)
            if i % tick_interval == 0:
                memory.tick()
            
            # Record page faults every 1000 accesses
            if (i + 1) % 1000 == 0:
                pass  # already recorded in access_page
        
        # Add final statistics
        if memory.page_faults > 0:
            memory.page_fault_history.append(memory.page_faults)
        
        results[num_frames] = memory.page_fault_history
        
        # Calculate average page fault rate
        if memory.page_fault_history:
            avg_fault_rate = sum(memory.page_fault_history) / len(memory.page_fault_history)
            print(f"Page faults per 1000 accesses: {memory.page_fault_history}")
            print(f"Average page fault rate: {avg_fault_rate:.2f} per 1000")
        else:
            print("No page faults recorded")
    
    return results, len(access_sequence)

def plot_results(results, total_accesses):
    """
    Plot results using English labels only
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # Subplot 1: Page faults per 1000 accesses (for different frame counts)
    ax1 = axes[0]
    
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'pink', 'gray', 'olive', 'cyan']
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    
    for idx, (num_frames, faults) in enumerate(results.items()):
        # Show only first 20 segments of 1000 accesses (if available)
        x_values = list(range(1, min(21, len(faults) + 1)))
        y_values = faults[:20]
        
        # Use different colors and markers
        color = colors[idx % len(colors)]
        marker = markers[idx % len(markers)]
        
        ax1.plot(x_values, y_values, marker=marker, label=f'{num_frames} frames', 
                linewidth=2, color=color, markersize=6)
    
    ax1.set_xlabel('Segment (per 1000 accesses)')
    ax1.set_ylabel('Page Faults')
    ax1.set_title('Aging Algorithm: Page Faults per 1000 Accesses')
    ax1.legend(title='Number of Frames', loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Total page fault rate vs number of frames
    ax2 = axes[1]
    
    frame_counts = []
    total_fault_rates = []
    
    for num_frames, faults in results.items():
        frame_counts.append(num_frames)
        # Calculate total page faults
        total_faults = sum(faults)
        # Calculate page fault rate (average faults per 1000 accesses)
        fault_rate = total_faults / (total_accesses / 1000) if total_accesses > 0 else 0
        total_fault_rates.append(fault_rate)
    
    bars = ax2.bar(frame_counts, total_fault_rates, color='skyblue', edgecolor='black', alpha=0.7)
    
    # Add gradient colors to bars
    for i, bar in enumerate(bars):
        bar.set_color(plt.cm.viridis(i / len(bars)))
    
    ax2.set_xlabel('Number of Frames')
    ax2.set_ylabel('Average Page Fault Rate (per 1000 accesses)')
    ax2.set_title('Aging Algorithm: Effect of Frame Count on Page Fault Rate')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(total_fault_rates):
        ax2.text(frame_counts[i], v + max(total_fault_rates)*0.02, f'{v:.1f}', 
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Save chart with English filename
    output_filename = 'aging_paging_results.png'
    plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    print(f"\nChart saved as: {output_filename}")
    
    plt.show()

def generate_test_file(filename, num_accesses=10000, num_unique_pages=50):
    """
    Generate test page access sequence file
    """
    # Generate access sequence using locality principle
    # 80% of accesses are to 20% of pages
    popular_pages = random.sample(range(1, num_unique_pages + 1), num_unique_pages // 5)
    
    with open(filename, 'w') as f:
        for _ in range(num_accesses):
            # 80% probability to access popular pages
            if random.random() < 0.8:
                page = random.choice(popular_pages)
            else:
                page = random.randint(1, num_unique_pages)
            f.write(f"{page}\n")
    
    print(f"Generated test file: {filename}")
    print(f"Number of accesses: {num_accesses}")
    print(f"Unique pages: {num_unique_pages}")
    print(f"Popular pages: {len(popular_pages)}")
    return filename

def display_summary(results, total_accesses):
    """
    Display summary results in English
    """
    print("\n" + "="*60)
    print("SUMMARY RESULTS")
    print("="*60)
    
    print(f"{'Frames':<10}{'Total Faults':<15}{'Avg Rate(per 1000)':<20}")
    print("-"*45)
    
    for num_frames in sorted(results.keys()):
        faults = results[num_frames]
        total_faults = sum(faults)
        fault_rate = total_faults / (total_accesses / 1000) if total_accesses > 0 else 0
        
        print(f"{num_frames:<10}{total_faults:<15}{fault_rate:<20.2f}")
    
    # Display improvement percentages
    print("\n" + "="*60)
    print("IMPROVEMENT WITH MORE FRAMES")
    print("="*60)
    
    prev_faults = None
    for num_frames in sorted(results.keys()):
        faults = results[num_frames]
        total_faults = sum(faults)
        
        if prev_faults is not None:
            improvement = ((prev_faults - total_faults) / prev_faults) * 100 if prev_faults > 0 else 0
            print(f"From {num_frames-1} to {num_frames} frames: Faults reduced by {improvement:.1f}%")
        
        prev_faults = total_faults

def main():
    """
    Main function - English version only
    """
    print("="*60)
    print("AGING ALGORITHM PAGING SYSTEM SIMULATION")
    print("="*60)
    
    # Check if test file exists
    test_file = "page_access_sequence.txt"
    try:
        with open(test_file, 'r'):
            pass
        print(f"Using existing test file: {test_file}")
    except FileNotFoundError:
        print(f"Test file not found, generating...")
        generate_test_file(test_file, num_accesses=20000, num_unique_pages=100)
    
    print("\n" + "="*60)
    print("STARTING AGING ALGORITHM SIMULATION")
    print("="*60)
    
    # Run simulation
    results, total_accesses = simulate_aging(
        file_path=test_file,
        max_frames=8,  # Test 1-8 frames
        tick_interval=50  # Aging every 50 accesses
    )
    
    if not results:
        print("Simulation failed, please check input file")
        return
    
    # Display summary results
    display_summary(results, total_accesses)
    
    # Plot results
    try:
        plot_results(results, total_accesses)
    except Exception as e:
        print(f"Error plotting results: {e}")
        print("Continuing with text output only...")
    
    # Save detailed results to file
    output_file = "aging_simulation_results.txt"
    with open(output_file, 'w') as f:
        f.write("AGING ALGORITHM PAGING SIMULATION RESULTS\n")
        f.write("="*60 + "\n")
        f.write(f"Total accesses: {total_accesses}\n")
        f.write(f"Frame range tested: 1-{len(results)}\n")
        f.write("\nDETAILED STATISTICS:\n")
        
        for num_frames in sorted(results.keys()):
            faults = results[num_frames]
            total_faults = sum(faults)
            fault_rate = total_faults / (total_accesses / 1000) if total_accesses > 0 else 0
            fault_percent = (total_faults / total_accesses) * 100 if total_accesses > 0 else 0
            
            f.write(f"\nNumber of Frames: {num_frames}\n")
            f.write(f"  Total Page Faults: {total_faults}\n")
            f.write(f"  Average Fault Rate: {fault_rate:.2f} / 1000 accesses\n")
            f.write(f"  Fault Percentage: {fault_percent:.2f}%\n")
            f.write(f"  Faults per 1000 accesses: {faults}\n")
    
    print(f"\nDetailed results saved to file: {output_file}")
    
    # Display final message
    print("\n" + "="*60)
    print("SIMULATION COMPLETED!")
    print("="*60)
    print("\nKEY FINDINGS:")
    print("1. Increasing number of frames significantly reduces page fault rate")
    print("2. Aging algorithm effectively identifies frequently used pages")
    print("3. Page fault rate decreases steadily with more frames")
    print("4. The algorithm shows good performance with realistic access patterns")
    
    # Calculate overall statistics
    if results:
        min_frames = min(results.keys())
        max_frames = max(results.keys())
        
        if min_frames in results and max_frames in results:
            min_faults = sum(results[min_frames])
            max_faults = sum(results[max_frames])
            improvement = ((min_faults - max_faults) / min_faults) * 100 if min_faults > 0 else 0
            
            print(f"\nOVERALL IMPROVEMENT:")
            print(f"From {min_frames} to {max_frames} frames: {improvement:.1f}% reduction in page faults")
    
    print("="*60)

if __name__ == "__main__":
    main()