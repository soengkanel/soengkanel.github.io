from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Nationality


class Command(BaseCommand):
    help = 'Populate nationality data with comprehensive country information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing nationality data before adding new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing nationality data...')
            Nationality.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Get the first superuser to set as created_by
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True).first()
        except:
            admin_user = None

        # Comprehensive nationality data - ALL UN Member States and Major Territories
        nationality_data = [
            # Southeast Asia
            ('855', 'KH', 'Cambodia', 'Cambodian', 'Southeast Asia'),
            ('66', 'TH', 'Thailand', 'Thai', 'Southeast Asia'),
            ('84', 'VN', 'Vietnam', 'Vietnamese', 'Southeast Asia'),
            ('62', 'ID', 'Indonesia', 'Indonesian', 'Southeast Asia'),
            ('60', 'MY', 'Malaysia', 'Malaysian', 'Southeast Asia'),
            ('63', 'PH', 'Philippines', 'Filipino', 'Southeast Asia'),
            ('95', 'MM', 'Myanmar', 'Burmese', 'Southeast Asia'),
            ('856', 'LA', 'Laos', 'Laotian', 'Southeast Asia'),
            ('65', 'SG', 'Singapore', 'Singaporean', 'Southeast Asia'),
            ('673', 'BN', 'Brunei', 'Bruneian', 'Southeast Asia'),
            ('670', 'TL', 'Timor-Leste', 'Timorese', 'Southeast Asia'),

            # East Asia
            ('86', 'CN', 'China', 'Chinese', 'East Asia'),
            ('81', 'JP', 'Japan', 'Japanese', 'East Asia'),
            ('82', 'KR', 'South Korea', 'Korean', 'East Asia'),
            ('886', 'TW', 'Taiwan', 'Taiwanese', 'East Asia'),
            ('853', 'MO', 'Macau', 'Macanese', 'East Asia'),
            ('976', 'MN', 'Mongolia', 'Mongolian', 'East Asia'),
            ('850', 'KP', 'North Korea', 'North Korean', 'East Asia'),
            ('852', 'HK', 'Hong Kong', 'Hong Konger', 'East Asia'),

            # South Asia
            ('91', 'IN', 'India', 'Indian', 'South Asia'),
            ('92', 'PK', 'Pakistan', 'Pakistani', 'South Asia'),
            ('880', 'BD', 'Bangladesh', 'Bangladeshi', 'South Asia'),
            ('94', 'LK', 'Sri Lanka', 'Sri Lankan', 'South Asia'),
            ('977', 'NP', 'Nepal', 'Nepalese', 'South Asia'),
            ('975', 'BT', 'Bhutan', 'Bhutanese', 'South Asia'),
            ('960', 'MV', 'Maldives', 'Maldivian', 'South Asia'),
            ('93', 'AF', 'Afghanistan', 'Afghan', 'South Asia'),

            # Middle East
            ('971', 'AE', 'United Arab Emirates', 'Emirati', 'Middle East'),
            ('966', 'SA', 'Saudi Arabia', 'Saudi', 'Middle East'),
            ('974', 'QA', 'Qatar', 'Qatari', 'Middle East'),
            ('965', 'KW', 'Kuwait', 'Kuwaiti', 'Middle East'),
            ('973', 'BH', 'Bahrain', 'Bahraini', 'Middle East'),
            ('968', 'OM', 'Oman', 'Omani', 'Middle East'),
            ('962', 'JO', 'Jordan', 'Jordanian', 'Middle East'),
            ('961', 'LB', 'Lebanon', 'Lebanese', 'Middle East'),
            ('963', 'SY', 'Syria', 'Syrian', 'Middle East'),
            ('964', 'IQ', 'Iraq', 'Iraqi', 'Middle East'),
            ('967', 'YE', 'Yemen', 'Yemeni', 'Middle East'),
            ('98', 'IR', 'Iran', 'Iranian', 'Middle East'),
            ('90', 'TR', 'Turkey', 'Turkish', 'Middle East'),
            ('972', 'IL', 'Israel', 'Israeli', 'Middle East'),
            ('995', 'GE', 'Georgia', 'Georgian', 'Middle East'),
            ('374', 'AM', 'Armenia', 'Armenian', 'Middle East'),
            ('994', 'AZ', 'Azerbaijan', 'Azerbaijani', 'Middle East'),
            ('357', 'CY', 'Cyprus', 'Cypriot', 'Middle East'),

            # Europe
            ('44', 'GB', 'United Kingdom', 'British', 'Europe'),
            ('33', 'FR', 'France', 'French', 'Europe'),
            ('49', 'DE', 'Germany', 'German', 'Europe'),
            ('3901', 'IT', 'Italy', 'Italian', 'Europe'),
            ('34', 'ES', 'Spain', 'Spanish', 'Europe'),
            ('351', 'PT', 'Portugal', 'Portuguese', 'Europe'),
            ('31', 'NL', 'Netherlands', 'Dutch', 'Europe'),
            ('32', 'BE', 'Belgium', 'Belgian', 'Europe'),
            ('41', 'CH', 'Switzerland', 'Swiss', 'Europe'),
            ('46', 'SE', 'Sweden', 'Swedish', 'Europe'),
            ('47', 'NO', 'Norway', 'Norwegian', 'Europe'),
            ('45', 'DK', 'Denmark', 'Danish', 'Europe'),
            ('358', 'FI', 'Finland', 'Finnish', 'Europe'),
            ('7', 'RU', 'Russia', 'Russian', 'Europe'),
            ('380', 'UA', 'Ukraine', 'Ukrainian', 'Europe'),
            ('48', 'PL', 'Poland', 'Polish', 'Europe'),
            ('30', 'GR', 'Greece', 'Greek', 'Europe'),
            ('43', 'AT', 'Austria', 'Austrian', 'Europe'),
            ('420', 'CZ', 'Czech Republic', 'Czech', 'Europe'),
            ('421', 'SK', 'Slovakia', 'Slovak', 'Europe'),
            ('36', 'HU', 'Hungary', 'Hungarian', 'Europe'),
            ('40', 'RO', 'Romania', 'Romanian', 'Europe'),
            ('359', 'BG', 'Bulgaria', 'Bulgarian', 'Europe'),
            ('385', 'HR', 'Croatia', 'Croatian', 'Europe'),
            ('386', 'SI', 'Slovenia', 'Slovenian', 'Europe'),
            ('387', 'BA', 'Bosnia and Herzegovina', 'Bosnian', 'Europe'),
            ('381', 'RS', 'Serbia', 'Serbian', 'Europe'),
            ('382', 'ME', 'Montenegro', 'Montenegrin', 'Europe'),
            ('383', 'XK', 'Kosovo', 'Kosovar', 'Europe'),
            ('389', 'MK', 'North Macedonia', 'Macedonian', 'Europe'),
            ('355', 'AL', 'Albania', 'Albanian', 'Europe'),
            ('372', 'EE', 'Estonia', 'Estonian', 'Europe'),
            ('371', 'LV', 'Latvia', 'Latvian', 'Europe'),
            ('370', 'LT', 'Lithuania', 'Lithuanian', 'Europe'),
            ('375', 'BY', 'Belarus', 'Belarusian', 'Europe'),
            ('373', 'MD', 'Moldova', 'Moldovan', 'Europe'),
            ('353', 'IE', 'Ireland', 'Irish', 'Europe'),
            ('354', 'IS', 'Iceland', 'Icelandic', 'Europe'),
            ('377', 'MC', 'Monaco', 'Monégasque', 'Europe'),
            ('378', 'SM', 'San Marino', 'Sammarinese', 'Europe'),
            ('3906', 'VA', 'Vatican City', 'Vatican', 'Europe'),
            ('376', 'AD', 'Andorra', 'Andorran', 'Europe'),
            ('423', 'LI', 'Liechtenstein', 'Liechtensteiner', 'Europe'),
            ('356', 'MT', 'Malta', 'Maltese', 'Europe'),
            ('298', 'FO', 'Faroe Islands', 'Faroese', 'Europe'),

            # Africa
            ('20', 'EG', 'Egypt', 'Egyptian', 'Africa'),
            ('27', 'ZA', 'South Africa', 'South African', 'Africa'),
            ('234', 'NG', 'Nigeria', 'Nigerian', 'Africa'),
            ('254', 'KE', 'Kenya', 'Kenyan', 'Africa'),
            ('233', 'GH', 'Ghana', 'Ghanaian', 'Africa'),
            ('251', 'ET', 'Ethiopia', 'Ethiopian', 'Africa'),
            ('212', 'MA', 'Morocco', 'Moroccan', 'Africa'),
            ('213', 'DZ', 'Algeria', 'Algerian', 'Africa'),
            ('216', 'TN', 'Tunisia', 'Tunisian', 'Africa'),
            ('218', 'LY', 'Libya', 'Libyan', 'Africa'),
            ('249', 'SD', 'Sudan', 'Sudanese', 'Africa'),
            ('256', 'UG', 'Uganda', 'Ugandan', 'Africa'),
            ('255', 'TZ', 'Tanzania', 'Tanzanian', 'Africa'),
            ('260', 'ZM', 'Zambia', 'Zambian', 'Africa'),
            ('263', 'ZW', 'Zimbabwe', 'Zimbabwean', 'Africa'),
            ('267', 'BW', 'Botswana', 'Botswanan', 'Africa'),
            ('268', 'SZ', 'Eswatini', 'Swazi', 'Africa'),
            ('266', 'LS', 'Lesotho', 'Basotho', 'Africa'),
            ('264', 'NA', 'Namibia', 'Namibian', 'Africa'),
            ('258', 'MZ', 'Mozambique', 'Mozambican', 'Africa'),
            ('261', 'MG', 'Madagascar', 'Malagasy', 'Africa'),
            ('230', 'MU', 'Mauritius', 'Mauritian', 'Africa'),
            ('248', 'SC', 'Seychelles', 'Seychellois', 'Africa'),
            ('269', 'KM', 'Comoros', 'Comorian', 'Africa'),
            ('262', 'RE', 'Réunion', 'Réunionese', 'Africa'),
            ('265', 'MW', 'Malawi', 'Malawian', 'Africa'),
            ('250', 'RW', 'Rwanda', 'Rwandan', 'Africa'),
            ('257', 'BI', 'Burundi', 'Burundian', 'Africa'),
            ('253', 'DJ', 'Djibouti', 'Djiboutian', 'Africa'),
            ('252', 'SO', 'Somalia', 'Somali', 'Africa'),
            ('291', 'ER', 'Eritrea', 'Eritrean', 'Africa'),
            ('211', 'SS', 'South Sudan', 'South Sudanese', 'Africa'),
            ('235', 'TD', 'Chad', 'Chadian', 'Africa'),
            ('236', 'CF', 'Central African Republic', 'Central African', 'Africa'),
            ('237', 'CM', 'Cameroon', 'Cameroonian', 'Africa'),
            ('240', 'GQ', 'Equatorial Guinea', 'Equatoguinean', 'Africa'),
            ('241', 'GA', 'Gabon', 'Gabonese', 'Africa'),
            ('242', 'CG', 'Republic of the Congo', 'Congolese', 'Africa'),
            ('243', 'CD', 'Democratic Republic of the Congo', 'Congolese', 'Africa'),
            ('244', 'AO', 'Angola', 'Angolan', 'Africa'),
            ('245', 'GW', 'Guinea-Bissau', 'Bissau-Guinean', 'Africa'),
            ('224', 'GN', 'Guinea', 'Guinean', 'Africa'),
            ('232', 'SL', 'Sierra Leone', 'Sierra Leonean', 'Africa'),
            ('231', 'LR', 'Liberia', 'Liberian', 'Africa'),
            ('225', 'CI', 'Côte d\'Ivoire', 'Ivorian', 'Africa'),
            ('226', 'BF', 'Burkina Faso', 'Burkinabé', 'Africa'),
            ('223', 'ML', 'Mali', 'Malian', 'Africa'),
            ('227', 'NE', 'Niger', 'Nigerien', 'Africa'),
            ('228', 'TG', 'Togo', 'Togolese', 'Africa'),
            ('229', 'BJ', 'Benin', 'Beninese', 'Africa'),

            # Americas - North America
            ('10001', 'US', 'United States', 'American', 'North America'),
            ('10002', 'CA', 'Canada', 'Canadian', 'North America'),
            ('52', 'MX', 'Mexico', 'Mexican', 'North America'),
            ('502', 'GT', 'Guatemala', 'Guatemalan', 'Central America'),
            ('503', 'SV', 'El Salvador', 'Salvadoran', 'Central America'),
            ('504', 'HN', 'Honduras', 'Honduran', 'Central America'),
            ('505', 'NI', 'Nicaragua', 'Nicaraguan', 'Central America'),
            ('506', 'CR', 'Costa Rica', 'Costa Rican', 'Central America'),
            ('507', 'PA', 'Panama', 'Panamanian', 'Central America'),
            ('501', 'BZ', 'Belize', 'Belizean', 'Central America'),

            # Americas - South America
            ('55', 'BR', 'Brazil', 'Brazilian', 'South America'),
            ('54', 'AR', 'Argentina', 'Argentine', 'South America'),
            ('56', 'CL', 'Chile', 'Chilean', 'South America'),
            ('57', 'CO', 'Colombia', 'Colombian', 'South America'),
            ('51', 'PE', 'Peru', 'Peruvian', 'South America'),
            ('58', 'VE', 'Venezuela', 'Venezuelan', 'South America'),
            ('593', 'EC', 'Ecuador', 'Ecuadorian', 'South America'),
            ('591', 'BO', 'Bolivia', 'Bolivian', 'South America'),
            ('595', 'PY', 'Paraguay', 'Paraguayan', 'South America'),
            ('598', 'UY', 'Uruguay', 'Uruguayan', 'South America'),
            ('592', 'GY', 'Guyana', 'Guyanese', 'South America'),
            ('597', 'SR', 'Suriname', 'Surinamese', 'South America'),
            ('594', 'GF', 'French Guiana', 'French Guianese', 'South America'),

            # Caribbean
            ('53', 'CU', 'Cuba', 'Cuban', 'Caribbean'),
            ('10809', 'DO', 'Dominican Republic', 'Dominican', 'Caribbean'),
            ('509', 'HT', 'Haiti', 'Haitian', 'Caribbean'),
            ('10242', 'BS', 'Bahamas', 'Bahamian', 'Caribbean'),
            ('10246', 'BB', 'Barbados', 'Barbadian', 'Caribbean'),
            ('10876', 'JM', 'Jamaica', 'Jamaican', 'Caribbean'),
            ('10868', 'TT', 'Trinidad and Tobago', 'Trinidadian', 'Caribbean'),
            ('10784', 'VC', 'Saint Vincent and the Grenadines', 'Vincentian', 'Caribbean'),
            ('10758', 'KN', 'Saint Kitts and Nevis', 'Kittitian', 'Caribbean'),
            ('10664', 'MS', 'Montserrat', 'Montserratian', 'Caribbean'),
            ('10473', 'GD', 'Grenada', 'Grenadian', 'Caribbean'),
            ('10268', 'AG', 'Antigua and Barbuda', 'Antiguan', 'Caribbean'),
            ('10721', 'SX', 'Sint Maarten', 'Sint Maartener', 'Caribbean'),
            ('508', 'PM', 'Saint Pierre and Miquelon', 'Saint-Pierrais', 'Caribbean'),

            # Oceania
            ('61', 'AU', 'Australia', 'Australian', 'Oceania'),
            ('64', 'NZ', 'New Zealand', 'New Zealander', 'Oceania'),
            ('679', 'FJ', 'Fiji', 'Fijian', 'Oceania'),
            ('675', 'PG', 'Papua New Guinea', 'Papua New Guinean', 'Oceania'),
            ('685', 'WS', 'Samoa', 'Samoan', 'Oceania'),
            ('676', 'TO', 'Tonga', 'Tongan', 'Oceania'),
            ('678', 'VU', 'Vanuatu', 'Vanuatuan', 'Oceania'),
            ('686', 'KI', 'Kiribati', 'I-Kiribati', 'Oceania'),
            ('687', 'NC', 'New Caledonia', 'New Caledonian', 'Oceania'),
            ('689', 'PF', 'French Polynesia', 'French Polynesian', 'Oceania'),
            ('682', 'CK', 'Cook Islands', 'Cook Islander', 'Oceania'),
            ('683', 'NU', 'Niue', 'Niuean', 'Oceania'),
            ('684', 'AS', 'American Samoa', 'American Samoan', 'Oceania'),
            ('691', 'FM', 'Micronesia', 'Micronesian', 'Oceania'),
            ('692', 'MH', 'Marshall Islands', 'Marshallese', 'Oceania'),
            ('680', 'PW', 'Palau', 'Palauan', 'Oceania'),
            ('688', 'TV', 'Tuvalu', 'Tuvaluan', 'Oceania'),
            ('674', 'NR', 'Nauru', 'Nauruan', 'Oceania'),
            ('50801', 'TF', 'French Southern Territories', 'French', 'Oceania'),

            # Central Asia
            ('998', 'UZ', 'Uzbekistan', 'Uzbek', 'Central Asia'),
            ('996', 'KG', 'Kyrgyzstan', 'Kyrgyz', 'Central Asia'),
            ('992', 'TJ', 'Tajikistan', 'Tajik', 'Central Asia'),
            ('99301', 'TM', 'Turkmenistan', 'Turkmen', 'Central Asia'),
            ('77', 'KZ', 'Kazakhstan', 'Kazakh', 'Central Asia'),
        ]

        self.stdout.write('Creating nationality records...')

        created_count = 0
        updated_count = 0

        for zip_code, country_code, country_name, nationality, region in nationality_data:
            nationality_obj, created = Nationality.objects.get_or_create(
                country_code=country_code,
                defaults={
                    'zip_code': zip_code,
                    'country_name': country_name,
                    'nationality': nationality,
                    'region': region,
                    'created_by': admin_user
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'Created: {country_name} ({country_code})')
            else:
                # Update existing record if data differs
                updated_fields = []
                if nationality_obj.zip_code != zip_code:
                    nationality_obj.zip_code = zip_code
                    updated_fields.append('zip_code')
                if nationality_obj.country_name != country_name:
                    nationality_obj.country_name = country_name
                    updated_fields.append('country_name')
                if nationality_obj.nationality != nationality:
                    nationality_obj.nationality = nationality
                    updated_fields.append('nationality')
                if nationality_obj.region != region:
                    nationality_obj.region = region
                    updated_fields.append('region')

                if updated_fields:
                    nationality_obj.save()
                    updated_count += 1
                    self.stdout.write(f'Updated: {country_name} ({country_code}) - {", ".join(updated_fields)}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed nationality data: '
                f'{created_count} created, {updated_count} updated'
            )
        )

        total_count = Nationality.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Total nationalities in database: {total_count}')
        )