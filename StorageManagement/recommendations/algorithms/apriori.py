# recommendations/apriori_algorithm.py

import pandas as pd
import itertools
from collections import defaultdict
from django.conf import settings
import os
from recommendations.models import AssociationRule, RuleProduct
from products.models import Product


def generateCandidate(itemsets, k):
    """Generate candidate k-itemsets from the given itemsets."""
    candidates = []
    itemsets = [set(itemset) for itemset in itemsets]

    for i in range(len(itemsets)):
        for j in range(i + 1, len(itemsets)):
            # Union of two itemsets
            candidate = itemsets[i] | itemsets[j]
            if len(candidate) == k:
                candidate_tuple = tuple(sorted(candidate))
                if candidate_tuple not in candidates:
                    # Check if all (k-1) subsets are frequent
                    subsets = list(itertools.combinations(candidate_tuple, k - 1))
                    if all(tuple(sorted(subset)) in [tuple(sorted(itemset)) for itemset in itemsets] for subset in
                           subsets):
                        candidates.append(candidate_tuple)
    return candidates


def calculateItemsetSupport(itemsets, transactions):
    """Calculate the support count of each itemset in the transactions."""
    itemset_support = {}

    for itemset in itemsets:
        count = 0
        itemset_set = set(itemset)

        for transaction in transactions:
            transaction_set = set(transaction)
            if itemset_set.issubset(transaction_set):
                count += 1

        itemset_support[itemset] = count

    return itemset_support


def removeItemset(itemsets_support, min_support):
    """Remove itemsets that do not meet the minimum support threshold."""
    frequent_itemsets = []
    for itemset, support in itemsets_support.items():
        if support >= min_support:
            frequent_itemsets.append(itemset)
    return frequent_itemsets


def calculateLift(antecedent_support, consequent_support, rule_support, total_transactions):
    """Calculate lift for association rule."""
    if antecedent_support == 0 or consequent_support == 0:
        return 0

    # Convert counts to probabilities
    prob_antecedent = antecedent_support / total_transactions
    prob_consequent = consequent_support / total_transactions
    prob_rule = rule_support / total_transactions

    # Lift = P(A ∪ B) / (P(A) * P(B))
    expected_support = prob_antecedent * prob_consequent
    if expected_support == 0:
        return 0

    return prob_rule / expected_support


def generateAssociationRules(frequent_itemsets_with_support, transactions, min_conf):
    """Generate association rules from frequent itemsets based on minimum confidence."""
    rules = []
    total_transactions = len(transactions)

    # Create a lookup for frequent itemsets support
    frequent_lookup = {}
    for itemsets_list in frequent_itemsets_with_support:
        for itemset, support in itemsets_list.items():
            frequent_lookup[itemset] = support

    # Generate rules from itemsets with length >= 2
    for itemsets_list in frequent_itemsets_with_support:
        for itemset, itemset_support in itemsets_list.items():
            if len(itemset) < 2:
                continue

            # Generate all possible antecedent-consequent pairs
            for i in range(1, len(itemset)):
                for antecedent in itertools.combinations(itemset, i):
                    antecedent = tuple(sorted(antecedent))
                    consequent = tuple(sorted(set(itemset) - set(antecedent)))

                    if not consequent:
                        continue

                    # Get supports
                    antecedent_support = frequent_lookup.get(antecedent, 0)
                    consequent_support = frequent_lookup.get(consequent, 0)

                    # Calculate confidence
                    if antecedent_support > 0:
                        confidence = itemset_support / antecedent_support
                    else:
                        confidence = 0

                    if confidence >= min_conf:
                        # Calculate lift
                        lift = calculateLift(antecedent_support, consequent_support,
                                             itemset_support, total_transactions)

                        rules.append({
                            'antecedent': antecedent,
                            'consequent': consequent,
                            'support': itemset_support / total_transactions,
                            'confidence': confidence,
                            'lift': lift,
                            'antecedent_support': antecedent_support,
                            'consequent_support': consequent_support,
                            'rule_support': itemset_support
                        })

    return rules


def apriori(transactions, unique_items, max_k, min_support):
    """Apriori algorithm for frequent itemset generation."""
    print(f"Starting Apriori with {len(transactions)} transactions, {len(unique_items)} unique items")

    # Generate 1-itemsets
    itemsets_1 = [(item,) for item in unique_items]
    itemsets_1_support = calculateItemsetSupport(itemsets_1, transactions)
    frequent_1 = removeItemset(itemsets_1_support, min_support)

    print(f"Frequent 1-itemsets: {len(frequent_1)} items")

    all_frequent_itemsets = [{itemset: itemsets_1_support[itemset] for itemset in frequent_1}]
    current_frequent = frequent_1

    # Generate k-itemsets (k >= 2)
    for k in range(2, max_k + 1):
        if not current_frequent:
            break

        # Generate candidates
        candidates = generateCandidate(current_frequent, k)

        if not candidates:
            break

        print(f"Generated {len(candidates)} candidate {k}-itemsets")

        # Calculate support for candidates
        candidate_support = calculateItemsetSupport(candidates, transactions)

        # Remove infrequent itemsets
        frequent_k = removeItemset(candidate_support, min_support)

        if not frequent_k:
            break

        print(f"Frequent {k}-itemsets: {len(frequent_k)} items")

        all_frequent_itemsets.append({itemset: candidate_support[itemset] for itemset in frequent_k})
        current_frequent = frequent_k

    return all_frequent_itemsets


def extract_frequent_patterns(min_support=0.01, min_confidence=0.5, max_k=3):
    """Extract frequent patterns from order data and save to database."""
    csv_file_path = 'recommendations/data/order_items_data.csv'

    try:
        # Load and preprocess data
        print("Loading data...")
        data = pd.read_csv(csv_file_path)

        # Group products by order_id to create transactions
        print("Creating transactions...")
        transactions_df = data.groupby('order_id')['product_name'].apply(list).reset_index()
        transactions = transactions_df['product_name'].tolist()

        # Remove empty transactions and clean data
        transactions = [
            [item.strip() for item in transaction if item and str(item).strip() != 'nan']
            for transaction in transactions if transaction
        ]
        transactions = [t for t in transactions if len(t) > 0]

        print(f"Created {len(transactions)} transactions")

        # Get unique items
        unique_items = set()
        for transaction in transactions:
            unique_items.update(transaction)
        unique_items = list(unique_items)

        print(f"Found {len(unique_items)} unique products")

        # Set parameters
        min_support = max(1, len(transactions) * 0.01)  # At least 1% support
        max_k = 3  # Maximum itemset size
        min_confidence = 0.5  # Minimum confidence for rules

        print(f"Parameters: min_support={min_support}, max_k={max_k}, min_confidence={min_confidence}")

        # Run Apriori algorithm
        print("Running Apriori algorithm...")
        frequent_itemsets = apriori(transactions, unique_items, max_k, min_support)

        # Generate association rules
        print("Generating association rules...")
        rules = generateAssociationRules(frequent_itemsets, transactions, min_confidence)

        print(f"Generated {len(rules)} association rules")

        # Clear existing rules
        print("Clearing existing rules...")
        AssociationRule.objects.all().delete()

        # Save rules to database
        print("Saving rules to database...")
        saved_count = 0

        for rule_data in rules:
            try:
                # Create association rule
                association_rule = AssociationRule.objects.create(
                    support=rule_data['support'],
                    confidence=rule_data['confidence'],
                    lift=rule_data['lift']
                )

                # Add antecedent products
                for product_name in rule_data['antecedent']:
                    product, created = Product.objects.get_or_create(
                        name=product_name,
                        defaults={'description': f'Product: {product_name}'}
                    )

                    RuleProduct.objects.create(
                        rule=association_rule,
                        product=product,
                        is_antecedent=True
                    )

                # Add consequent products
                for product_name in rule_data['consequent']:
                    product, created = Product.objects.get_or_create(
                        name=product_name,
                        defaults={'description': f'Product: {product_name}'}
                    )

                    RuleProduct.objects.create(
                        rule=association_rule,
                        product=product,
                        is_antecedent=False
                    )

                saved_count += 1

            except Exception as e:
                print(f"Error saving rule: {e}")
                continue

        print(f"Successfully saved {saved_count} association rules to database")

        # Print sample results
        print("\nSample Association Rules:")
        for i, rule in enumerate(rules[:5]):
            antecedent_str = ", ".join(rule['antecedent'])
            consequent_str = ", ".join(rule['consequent'])
            print(f"{i + 1}. {antecedent_str} -> {consequent_str}")
            print(f"   Support: {rule['support']:.3f}, Confidence: {rule['confidence']:.3f}, Lift: {rule['lift']:.3f}")

        return {
            'success': True,
            'total_rules': len(rules),
            'saved_rules': saved_count,
            'total_transactions': len(transactions),
            'unique_products': len(unique_items)
        }

    except Exception as e:
        print(f"Error in extract_frequent_patterns: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def get_product_recommendations(product_names, limit=5):
    """Get product recommendations based on association rules."""
    if not product_names:
        return []

    try:
        # Find rules where any of the input products are in antecedent
        antecedent_rules = AssociationRule.objects.filter(
            products__product__name__in=product_names,
            products__is_antecedent=True
        ).distinct().order_by('-lift', '-confidence')

        recommendations = []
        seen_products = set(product_names)

        for rule in antecedent_rules[:limit * 2]:  # Get more to filter
            # Get consequent products for this rule
            consequent_products = rule.products.filter(is_antecedent=False)

            for rule_product in consequent_products:
                if rule_product.product.name not in seen_products:
                    recommendations.append({
                        'product': rule_product.product,
                        'confidence': rule.confidence,
                        'lift': rule.lift,
                        'support': rule.support
                    })
                    seen_products.add(rule_product.product.name)

                    if len(recommendations) >= limit:
                        break

            if len(recommendations) >= limit:
                break

        return recommendations[:limit]

    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []


# Test function
def test_apriori():
    """Test the Apriori implementation."""
    result = extract_frequent_patterns()
    print("Test Results:", result)

    # Test recommendations
    if result['success']:
        sample_products = ['محصول 4', 'محصول 6']
        recommendations = get_product_recommendations(sample_products)
        print(f"\nRecommendations for {sample_products}:")
        for rec in recommendations:
            print(f"- {rec['product'].name} (Confidence: {rec['confidence']:.3f}, Lift: {rec['lift']:.3f})")


if __name__ == "__main__":
    test_apriori()