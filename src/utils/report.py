"""Report generation utilities."""
from datetime import datetime


def generate_report(results):
    """Generate a text report from analysis results."""
    report = []
    report.append("=" * 80)
    report.append("SRS AMBIGUITY ANALYSIS REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    total = len(results)
    clear_count = sum(1 for r in results if r.get('label') in ['Clear', 'Clean', 'LABEL_0'])
    ambiguous_count = total - clear_count
    
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Requirements: {total}")
    report.append(f"Clear Requirements: {clear_count}")
    report.append(f"Ambiguous Requirements: {ambiguous_count}")
    report.append(f"Ambiguity Rate: {(ambiguous_count/total*100):.1f}%")
    report.append("")
    
    # Detailed Results
    report.append("DETAILED RESULTS")
    report.append("=" * 80)
    report.append("")
    
    for idx, result in enumerate(results, 1):
        report.append(f"Requirement {idx}")
        report.append("-" * 80)
        report.append(f"Original: {result['sentence']}")
        report.append(f"Status: {result['label']}")
        report.append(f"Confidence: {result['score']:.2%}")
        report.append("")
        
        if result.get('rewrite'):
            report.append(f"Suggested Rewrite: {result['rewrite']}")
            report.append("")
        
        if result.get('evidence'):
            report.append("Retrieved Context:")
            for i, item in enumerate(result['evidence'], 1):
                source = item.get('source', 'Unknown')
                content_type = item.get('content_type', item.get('type', 'General'))
                page = item.get('page', 'N/A')
                report.append(f"  {i}. {source} ({content_type}) - Page: {page}")
            report.append("")
        
        report.append("")
    
    return "\n".join(report)

