# recommendations/management/commands/frequent_pattern_mining.py

from django.core.management.base import BaseCommand
from recommendations.algorithms.apriori import extract_frequent_patterns


class Command(BaseCommand):
    help = 'Extract frequent patterns using Apriori algorithm and save association rules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-support',
            type=float,
            default=0.01,
            help='Minimum support threshold (default: 0.01 = 1%)'
        )
        parser.add_argument(
            '--min-confidence',
            type=float,
            default=0.5,
            help='Minimum confidence threshold (default: 0.5 = 50%)'
        )
        parser.add_argument(
            '--max-itemset-size',
            type=int,
            default=3,
            help='Maximum itemset size (default: 3)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Apriori algorithm...')
        )

        try:
            result = extract_frequent_patterns(
                min_support=options['min_support'],
                min_confidence=options['min_confidence'],
                max_k=options['max_itemset_size']
            )

            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully completed!\n'
                        f'Total transactions: {result["total_transactions"]}\n'
                        f'Unique products: {result["unique_products"]}\n'
                        f'Total rules generated: {result["total_rules"]}\n'
                        f'Rules saved to database: {result["saved_rules"]}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Error: {result["error"]}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {str(e)}')
            )