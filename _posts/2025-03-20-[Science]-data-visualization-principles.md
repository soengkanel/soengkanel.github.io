---
layout: post
title: "[Science] Data Visualization: Principles for Clear Communication"
tags: [Data Visualization, Communication, Graphics, Best Practices]
---

Effective visualization transforms data into insight. Poor visualization obscures or misleads. This article presents principles for honest, clear scientific graphics.

## Core Principles

### 1. Show the Data

The primary purpose is revealing what the data contains.

**Do**:
- Show individual data points when feasible
- Use appropriate scales
- Include uncertainty measures

**Don't**:
- Hide data behind aggregates unnecessarily
- Use 3D when 2D suffices
- Add decorative elements that obscure

### 2. Maximize Data-Ink Ratio

Edward Tufte's principle: Maximize the proportion of ink devoted to data.

```
Data-ink ratio = Data ink / Total ink

Remove:
- Unnecessary gridlines
- Redundant labels
- Decorative elements
- Chart junk
```

### 3. Maintain Proportionality

Visual representation should match numerical relationships.

**Common violations**:
- Truncated y-axes (exaggerate differences)
- Area/volume encoding (misjudged by viewers)
- Dual y-axes (misleading correlations)

## Chart Selection Guide

| Data Type | Comparison | Chart Type |
|-----------|------------|------------|
| Categorical | Values | Bar chart |
| Categorical | Proportions | Stacked bar, pie (if few categories) |
| Continuous | Distribution | Histogram, density plot |
| Two continuous | Relationship | Scatter plot |
| Time series | Trend | Line chart |
| Grouped continuous | Distributions | Box plot, violin plot |

### When to Use What

**Bar charts**: Comparing discrete categories
```
✓ Sales by region
✓ Counts by category
✗ Continuous distributions
```

**Line charts**: Continuous data, especially time
```
✓ Stock prices over time
✓ Temperature trends
✗ Categorical comparisons
```

**Scatter plots**: Two continuous variables
```
✓ Height vs. weight
✓ Correlation exploration
✗ Categorical data
```

**Box plots**: Distribution comparison
```
✓ Comparing groups
✓ Showing spread and outliers
✗ When sample size matters
```

## Encoding Channels

Visual properties ranked by perceptual accuracy:

**Quantitative data**:
1. Position (most accurate)
2. Length
3. Angle
4. Area
5. Color intensity (least accurate)

**Categorical data**:
1. Position
2. Color hue
3. Shape
4. Texture

Use higher-ranked channels for most important variables.

## Color Usage

### Perceptual Principles

**Sequential**: Ordered data (low → high)
- Single hue, varying lightness
- Example: Light blue → Dark blue

**Diverging**: Data with meaningful midpoint
- Two hues meeting at neutral
- Example: Blue → White → Red

**Categorical**: Distinct groups
- Different hues, similar saturation
- Avoid: Red-green together (colorblindness)

### Colorblindness Considerations

8% of males have color vision deficiency.

**Safe palettes**:
- Blue-orange (instead of red-green)
- Use shapes/patterns in addition to color
- Test with colorblindness simulators

## Showing Uncertainty

Always communicate uncertainty in scientific figures.

**Methods**:
- Error bars (SE or 95% CI)
- Confidence bands
- Density plots
- Individual data points

**Error bar conventions**:
```
Clearly label what error bars represent:
- Standard deviation (data spread)
- Standard error (precision of mean)
- 95% CI (inferential)
```

## Common Mistakes

### Misleading Practices

**Truncated axes**:
```
Bad:  Y-axis starting at 95 makes 98 vs 96 look huge
Good: Y-axis from 0, or clearly indicate break
```

**Cherry-picked time windows**:
```
Bad:  Show only period where trend supports claim
Good: Show full available time range
```

**Dual y-axes**:
```
Bad:  Two different scales suggest false correlation
Good: Separate panels or normalize scales
```

### Technical Errors

**Overplotting**: Too many points obscure patterns
- Solution: Transparency, binning, sampling

**Poor aspect ratio**: Distorts trends
- Solution: Bank to 45° (line slopes ~45°)

**Excessive precision**: False sense of accuracy
- Solution: Round appropriately

## Practical Checklist

```
Before finalizing a figure:

[ ] Does the chart type match the data?
[ ] Is the message immediately clear?
[ ] Are axes properly labeled with units?
[ ] Is uncertainty shown?
[ ] Are colors accessible (colorblind-safe)?
[ ] Is the data-ink ratio high?
[ ] Are scales honest (not truncated misleadingly)?
[ ] Can it stand alone (legend, labels complete)?
```

## Conclusion

Good visualization is honest communication. Every design choice should serve clarity, not decoration. When in doubt, simplify and show more of the actual data.
