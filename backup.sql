PGDMP      1                }            deneme2    17.5    17.5 !    D           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            E           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            F           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            G           1262    24988    deneme2    DATABASE     �   CREATE DATABASE deneme2 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1254';
    DROP DATABASE deneme2;
                     postgres    false            �            1259    25002 	   employers    TABLE     g  CREATE TABLE public.employers (
    id integer NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    company_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.employers;
       public         heap r       postgres    false            �            1259    25001    employers_id_seq    SEQUENCE     �   CREATE SEQUENCE public.employers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.employers_id_seq;
       public               postgres    false    220            H           0    0    employers_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.employers_id_seq OWNED BY public.employers.id;
          public               postgres    false    219            �            1259    25028 	   favorites    TABLE     �   CREATE TABLE public.favorites (
    student_id integer NOT NULL,
    job_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.favorites;
       public         heap r       postgres    false            �            1259    25014    jobs    TABLE     _  CREATE TABLE public.jobs (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text NOT NULL,
    working_days character varying(255) NOT NULL,
    working_hours character varying(255) NOT NULL,
    total_hours real NOT NULL,
    daily_salary integer NOT NULL,
    hourly_salary real,
    job_duration character varying(100) NOT NULL,
    job_type character varying(100) NOT NULL,
    location character varying(255) NOT NULL,
    contact_email character varying(255),
    employer_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.jobs;
       public         heap r       postgres    false            �            1259    25013    jobs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.jobs_id_seq;
       public               postgres    false    222            I           0    0    jobs_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;
          public               postgres    false    221            �            1259    24990    students    TABLE     D  CREATE TABLE public.students (
    id integer NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    school_email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.students;
       public         heap r       postgres    false            �            1259    24989    students_id_seq    SEQUENCE     �   CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.students_id_seq;
       public               postgres    false    218            J           0    0    students_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;
          public               postgres    false    217            �           2604    25005    employers id    DEFAULT     l   ALTER TABLE ONLY public.employers ALTER COLUMN id SET DEFAULT nextval('public.employers_id_seq'::regclass);
 ;   ALTER TABLE public.employers ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    219    220    220            �           2604    25017    jobs id    DEFAULT     b   ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);
 6   ALTER TABLE public.jobs ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    222    221    222            �           2604    24993    students id    DEFAULT     j   ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);
 :   ALTER TABLE public.students ALTER COLUMN id DROP DEFAULT;
       public               postgres    false    217    218    218            >          0    25002 	   employers 
   TABLE DATA           n   COPY public.employers (id, first_name, last_name, email, password_hash, company_name, created_at) FROM stdin;
    public               postgres    false    220   �(       A          0    25028 	   favorites 
   TABLE DATA           C   COPY public.favorites (student_id, job_id, created_at) FROM stdin;
    public               postgres    false    223   �+       @          0    25014    jobs 
   TABLE DATA           �   COPY public.jobs (id, title, description, working_days, working_hours, total_hours, daily_salary, hourly_salary, job_duration, job_type, location, contact_email, employer_id, created_at) FROM stdin;
    public               postgres    false    222   y,       <          0    24990    students 
   TABLE DATA           f   COPY public.students (id, first_name, last_name, school_email, password_hash, created_at) FROM stdin;
    public               postgres    false    218   Q4       K           0    0    employers_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.employers_id_seq', 30, true);
          public               postgres    false    219            L           0    0    jobs_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.jobs_id_seq', 31, true);
          public               postgres    false    221            M           0    0    students_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.students_id_seq', 5, true);
          public               postgres    false    217            �           2606    25012    employers employers_email_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.employers
    ADD CONSTRAINT employers_email_key UNIQUE (email);
 G   ALTER TABLE ONLY public.employers DROP CONSTRAINT employers_email_key;
       public                 postgres    false    220            �           2606    25010    employers employers_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.employers
    ADD CONSTRAINT employers_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.employers DROP CONSTRAINT employers_pkey;
       public                 postgres    false    220            �           2606    25033    favorites favorites_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (student_id, job_id);
 B   ALTER TABLE ONLY public.favorites DROP CONSTRAINT favorites_pkey;
       public                 postgres    false    223    223            �           2606    25022    jobs jobs_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.jobs DROP CONSTRAINT jobs_pkey;
       public                 postgres    false    222            �           2606    24998    students students_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.students DROP CONSTRAINT students_pkey;
       public                 postgres    false    218            �           2606    25000 "   students students_school_email_key 
   CONSTRAINT     e   ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_school_email_key UNIQUE (school_email);
 L   ALTER TABLE ONLY public.students DROP CONSTRAINT students_school_email_key;
       public                 postgres    false    218            �           2606    25039    favorites favorites_job_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;
 I   ALTER TABLE ONLY public.favorites DROP CONSTRAINT favorites_job_id_fkey;
       public               postgres    false    4772    223    222            �           2606    25034 #   favorites favorites_student_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;
 M   ALTER TABLE ONLY public.favorites DROP CONSTRAINT favorites_student_id_fkey;
       public               postgres    false    223    4764    218            �           2606    25023    jobs jobs_employer_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_employer_id_fkey FOREIGN KEY (employer_id) REFERENCES public.employers(id) ON DELETE CASCADE;
 D   ALTER TABLE ONLY public.jobs DROP CONSTRAINT jobs_employer_id_fkey;
       public               postgres    false    4770    222    220            >   9  x����n�@�ϓ���*q�6�D���HAj�Tm�M��ލ�ђ� /���s/���}/ƻk�C�%�R3c�����t��B�V?D
Xj���C}͙\���Y4y�Ì%3>���$�S1!��L�_w-�X�����N��y��y�-�I�(�K�?>�\��<\[�+A�p]�{���b��=S>����I�� ��@m�-*�T�|�T�n��p��@�"�Pm��K��Op��#yIL'
��9�X�KdFY���H���6Mr���%Cri�!�)�[���VmC!9�c|�����\���]\�a+K��'9ˢ�p���‍�lu�9U�	�������[���Ӭ�k��[��c����
9��In��r�Y�d@�e�p�d*�Ы���	���a���L����J���Dv�Չ��H�w��Lr\	�[�o֯�@�$%ө݇���(j^q�.sN��ͼ��n8�TŬ>��,�b<G�;�8�JX�� ��t�y~nG\��=<�ѩ�XЈ�9%��4f!ѳ.x U�!�M�깜��i�(����&ѱӾ�ZR�g-�]v�\��y��;i?�v��/Q�z��v^�%^8�����Eo��K��s[&3���ib��e�q����-&L�eq4G�ox6o���Lm�|�~� �x9HT@#m֗5$bIN�}\�,�o���Ǉ ����|��M/�gMڼC%��L� ^�ؘ�C�&���-liU����D���������5AZlsu�w����&6>+R`�-ěu��Zm�Fe	�]7^?���!��KF*�e�=�Vڴ�y�i_��U]�J[��?��      A   m   x�u���0C�0EHN�o��?GQ϶��Y/B&i0jD`�x��<C� 7`S�C�L(ܘ�?O^S� 7�]�߂'����Q��h���/՗V�/xww� 0Fk/      @   �  x��XMs�F=���*�@�tZ}fk9�8q�S��ȡ80P�[�������kt�7P�k�g$HD9�r2����~�z\�_H��?"������D]iĒ�j�Wk9��q��+���x�ԡ9�Y���ͪ��/b��9��e��9]��G1�D��gK�<]�q����yp%n��pܞO>T��F��y^��&�QK�:��2�{{�����1F=3������7N�������~�q�տ7y/�KP�E\l7�u����i��#��V���J�Cg��%��9��"?��
�{�X�9`��]io�t�/��xGߥ�aP�X0�Y#M�"N�Ha��X�z��,�����u�PJ:���_���7���0���tR�*�G�!�}+��	{��ӛXZboVtT}��|�L��(R�:tV����E�h��Q�a �A�sw��2(aee�q��c��	����"������"yFn
�`s���z�#��A�K�Xn�^��w�C��ͽ�uR^v]���<����!q��\搊D"
2b�9�| 7&'sQ}F�p�c���46p�$�4�{����
k�����	�(�䣐�^��2c9|}��h\�Wp�$E#�K�������I(�F
^��]�:<{�m����?$hh��ey�Bb�����3#��1I�h�,/��4�PU_Ҏ����*�Vy������d-�B;#Y�������nu�uj>:4c3V�x qϫ��4+X�y�&� �pઔ�б�����RYF|.�01����3+�!�i`��|�BI�'VS�
v����5�	��k��6]޶�����Z���
�% 4���S��=�V�-X�uT�`�[��TA�LܡB2p�u3�W7�ܠGq[��Y q��V;��Z��Y7��B�BHA>a�3�
D�!��e��E
�El��g�-�ǁK�o�R����WX���׸:�F4��RX�ޠ��4���/v� �*�����Rrl��|����TL���m�U�0�((�|�Z2'��+f��,���4���-#w�z��D䱈@��jc���L_[�{��ݵŞ$m<ػ���\�_hź�>���I�ߚ�E	_��lI,S����1���8��a���IW�h���Ҽc8Sj�k�X��1�3� �4�if0��/Hw,����:0������t:�-u¥.e\�R�9�"�L�x^�,x���n��m�����u`R�V�
q�Zx����\qYd�����4�Gd�S�Uj�4�x��n�˴�@[�C�]l/h*�e������a�����gw���h���5C�s�z/2
��|(�|��@V�{�f��o��w0�sp3H���=��U����s�~�75��j�}5�:��͉xOL�����yv�y���"���
���Dx���PB��L �b���N������!s|��#�6��x����}�8��Yė���T���k9©�ɭXBëik`����J`0�j��F[w���J�ի��_"r�/�i�\lV�|�n\�ᴸ�,���v��~� �ߪ���J�<}E��M�-��M���-&L��z�ԇ����:�4����FC��Qiiq�ւy9~�P����^�����4�6I^�8@A���¾�r_k�0���)C	�����ߡ�,~`�������'�I�~vY�wf����74���И4��A<|�l�&��tv#!�"��l��?ic�jo]6�}yl<���B�������i��Q��p�X
׻�֨�3��@0$��v�A��^��M�qI��Cj�>�ANbk}�ئFؼ��!���w�:�
,X��DuD�ݹAg���`���A���97i��no����˴��b�1�op�6���f��>���AJ�98+�����k�*�jv=@����f�ĺ-͠yz��]��`���yt�ow,��޼y���      <   �   x����� @��W8�J�8tRc�`� �PH�m�����a�a�Rû�^r9�Z?԰qP4�\�nt?pM�=t��nX=�B��p%�c�SWmZG��49�)(P.�\".���?C8j��^���	��Qgw�!%&;l[�p����.q�/�Ⱦg�
VPb�V��񺁝n��S�١�����p>��A�T�_t^�]�LRb�t�Y�� ��     