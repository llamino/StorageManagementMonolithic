# recommendations/apriori_algorithm.py

import pandas as pd
import itertools
from collections import defaultdict
from django.conf import settings
import os
from recommendations.models import AssociationRule, RuleProduct
from products.models import Product


def generateCandidate(itemsets, k):
    """تولید مجموعه‌های کاندید k-آیتمی از آیتم‌ست‌های قبلی"""
    candidates = []
    itemsets = [set(itemset) for itemset in itemsets]

    for i in range(len(itemsets)):
        for j in range(i + 1, len(itemsets)):
            # اجتماع دو آیتم‌ست
            candidate = itemsets[i] | itemsets[j]
            if len(candidate) == k:
                candidate_tuple = tuple(sorted(candidate))
                if candidate_tuple not in candidates:
                    # بررسی اینکه همه زیرمجموعه‌های (k-1) آیتمی در لیست آیتم‌ست‌ها هستند
                    subsets = list(itertools.combinations(candidate_tuple, k - 1))
                    if all(tuple(sorted(subset)) in [tuple(sorted(itemset)) for itemset in itemsets] for subset in subsets):
                        candidates.append(candidate_tuple)
    return candidates


def calculateItemsetSupport(itemsets, transactions):
    """محاسبه تعداد پشتیبانی هر آیتم‌ست در تراکنش‌ها"""
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
    """حذف آیتم‌ست‌هایی که پشتیبانی کافی ندارند"""
    frequent_itemsets = []
    for itemset, support in itemsets_support.items():
        if support >= min_support:
            frequent_itemsets.append(itemset)
    return frequent_itemsets


def calculateLift(antecedent_support, consequent_support, rule_support, total_transactions):
    """محاسبه معیار Lift برای قانون انجمنی"""
    if antecedent_support == 0 or consequent_support == 0:
        return 0

    # محاسبه احتمال‌ها
    prob_antecedent = antecedent_support / total_transactions
    prob_consequent = consequent_support / total_transactions
    prob_rule = rule_support / total_transactions

    # Lift = P(A ∪ B) / (P(A) * P(B))
    expected_support = prob_antecedent * prob_consequent
    if expected_support == 0:
        return 0

    return prob_rule / expected_support


def generateAssociationRules(frequent_itemsets_with_support, transactions, min_conf):
    """تولید قوانین انجمنی با حداقل اعتماد مشخص‌شده"""
    rules = []
    total_transactions = len(transactions)

    # ایجاد دیکشنری lookup برای پشتیبانی آیتم‌ست‌ها
    frequent_lookup = {}
    for itemsets_list in frequent_itemsets_with_support:
        for itemset, support in itemsets_list.items():
            frequent_lookup[itemset] = support

    # تولید قوانین از آیتم‌ست‌هایی با طول حداقل ۲
    for itemsets_list in frequent_itemsets_with_support:
        for itemset, itemset_support in itemsets_list.items():
            if len(itemset) < 2:
                continue

            # تولید تمام ترکیب‌های ممکن مقدم و تالی
            for i in range(1, len(itemset)):
                for antecedent in itertools.combinations(itemset, i):
                    antecedent = tuple(sorted(antecedent))
                    consequent = tuple(sorted(set(itemset) - set(antecedent)))

                    if not consequent:
                        continue

                    # گرفتن پشتیبانی‌ها
                    antecedent_support = frequent_lookup.get(antecedent, 0)
                    consequent_support = frequent_lookup.get(consequent, 0)

                    # محاسبه اعتماد
                    if antecedent_support > 0:
                        confidence = itemset_support / antecedent_support
                    else:
                        confidence = 0

                    # بررسی اینکه اعتماد از حداقل مقدار بیشتر باشد
                    if confidence >= min_conf:
                        lift = calculateLift(antecedent_support, consequent_support, itemset_support, total_transactions)

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
    """اجرای الگوریتم Apriori برای یافتن آیتم‌ست‌های پرتکرار"""
    print(f"Starting Apriori with {len(transactions)} transactions, {len(unique_items)} unique items")

    # ایجاد آیتم‌ست‌های تک‌عنصری
    itemsets_1 = [(item,) for item in unique_items]
    itemsets_1_support = calculateItemsetSupport(itemsets_1, transactions)
    frequent_1 = removeItemset(itemsets_1_support, min_support)

    print(f"Frequent 1-itemsets: {len(frequent_1)} items")

    all_frequent_itemsets = [{itemset: itemsets_1_support[itemset] for itemset in frequent_1}]
    current_frequent = frequent_1

    # ایجاد آیتم‌ست‌های با طول بیشتر
    for k in range(2, max_k + 1):
        if not current_frequent:
            break

        candidates = generateCandidate(current_frequent, k)

        if not candidates:
            break

        print(f"Generated {len(candidates)} candidate {k}-itemsets")

        candidate_support = calculateItemsetSupport(candidates, transactions)
        frequent_k = removeItemset(candidate_support, min_support)

        if not frequent_k:
            break

        print(f"Frequent {k}-itemsets: {len(frequent_k)} items")

        all_frequent_itemsets.append({itemset: candidate_support[itemset] for itemset in frequent_k})
        current_frequent = frequent_k

    return all_frequent_itemsets


def extract_frequent_patterns(min_support=0.01, min_confidence=0.5, max_k=3):
    """استخراج الگوهای پرتکرار و ذخیره در پایگاه داده"""
    csv_file_path = 'recommendations/data/order_items_data.csv'

    try:
        # بارگذاری داده‌ها
        print("Loading data...")
        data = pd.read_csv(csv_file_path)

        # ایجاد تراکنش‌ها بر اساس order_id
        print("Creating transactions...")
        transactions_df = data.groupby('order_id')['product_name'].apply(list).reset_index()
        transactions = transactions_df['product_name'].tolist()

        # حذف تراکنش‌های خالی
        transactions = [
            [item.strip() for item in transaction if item and str(item).strip() != 'nan']
            for transaction in transactions if transaction
        ]
        transactions = [t for t in transactions if len(t) > 0]

        print(f"Created {len(transactions)} transactions")

        # یافتن محصولات یکتا
        unique_items = set()
        for transaction in transactions:
            unique_items.update(transaction)
        unique_items = list(unique_items)

        print(f"Found {len(unique_items)} unique products")

        # تنظیم پارامترها
        min_support = max(1, len(transactions) * 0.01)
        max_k = 3
        min_confidence = 0.5

        print(f"Parameters: min_support={min_support}, max_k={max_k}, min_confidence={min_confidence}")

        # اجرای الگوریتم Apriori
        print("Running Apriori algorithm...")
        frequent_itemsets = apriori(transactions, unique_items, max_k, min_support)

        # تولید قوانین انجمنی
        print("Generating association rules...")
        rules = generateAssociationRules(frequent_itemsets, transactions, min_confidence)

        print(f"Generated {len(rules)} association rules")

        # حذف قوانین قبلی
        print("Clearing existing rules...")
        AssociationRule.objects.all().delete()

        # ذخیره قوانین جدید در پایگاه داده
        print("Saving rules to database...")
        saved_count = 0

        for rule_data in rules:
            try:
                association_rule = AssociationRule.objects.create(
                    support=rule_data['support'],
                    confidence=rule_data['confidence'],
                    lift=rule_data['lift']
                )

                # ذخیره محصولات مقدم
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

                # ذخیره محصولات تالی
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

        # چاپ چند قانون نمونه
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
    """دریافت توصیه محصول بر اساس قوانین انجمنی"""
    if not product_names:
        return []

    try:
        # یافتن قوانینی که ورودی‌ها در قسمت مقدم آن‌ها باشند
        antecedent_rules = AssociationRule.objects.filter(
            products__product__name__in=product_names,
            products__is_antecedent=True
        ).distinct().order_by('-lift', '-confidence')

        recommendations = []
        seen_products = set(product_names)

        for rule in antecedent_rules[:limit * 2]:
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


def test_apriori():
    """اجرای تست الگوریتم Apriori"""
    result = extract_frequent_patterns()
    print("Test Results:", result)

    if result['success']:
        sample_products = ['محصول 4', 'محصول 6']
        recommendations = get_product_recommendations(sample_products)
        print(f"\nRecommendations for {sample_products}:")
        for rec in recommendations:
            print(f"- {rec['product'].name} (Confidence: {rec['confidence']:.3f}, Lift: {rec['lift']:.3f})")


if __name__ == "__main__":
    test_apriori()
