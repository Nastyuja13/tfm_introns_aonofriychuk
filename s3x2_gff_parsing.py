import gzip

# Selects the correct gene_id from a split by ':' in gene or transcript attributes
def _select_id(attr_dict, id_key):

  # Differentiate if the id is for a gene or for a transcirpt (parent gene)
  #if 'gene_id' in atr_dict:
    #id_key = 'gene_id'
    #gene_id = atr_dict[id_key].split(':')[-1]
  #elif 'transcript_id' in atr_dict:
    #id_key = 'Parent'
    #gene_id = atr_dict[id_key].split(':')[-1]

  id_attr = attr_dict[id_key].split(':')

  #print(attr_dict)

  # Check needed as "Leishmania major" has gene IDs in this format: "ID=gene:LMJF_32_ncRNA2:ncRNA;"
  # Check needed as "Plasmodium chabaudi" has gene IDs with "ID=gene:PCHAS_113132:tRNA:tRNA;" 
  # or "gene:chab06_tRNA1:tRNA" or "ID=gene:chab5_18s:rRNA;" structure
  # Check needed as "Prunus avium" has transcript IDs in this format: "ID=transcript:Pav_co3990083.1_g010.1.mk:mrna;"
  # Check needed as "Plasmodium chabaudi" has transcript IDs with "ID=transcript:chab5_5.8s:rRNA-1;" format

  if (len(id_attr) == 1) or (len(id_attr) == 2):
    id_name = id_attr[-1]
  elif (len(id_attr) == 3):
    id_name = id_attr[-2] + ':' + id_attr[-1]
  else:
    id_name = id_attr[-3] + ':' + id_attr[-2] + ':' + id_attr[-1]

  #print(id_name)
  return id_name


# Parsing of the file
def parse_gff(gff_path):

  gene_dict = []
  trans_dict = []
  exon_dict = []

  try:
    #for line in open(gff_path, 'rt'):
    for line in gzip.open(gff_path, 'rt'):

      if line.startswith('#'):
        continue

      # obtain all info of the record
      fields = line.split('\t')
      seqid = fields[0]
      source = fields[1]
      seqtype = fields[2]
      start = int(fields[3])
      end = int(fields[4])
      score = fields[5]
      strand = fields[6]
      phase = fields[7]
      attributes = dict([attribute.split('=') for attribute in fields[-1].strip('\n').split(';')])
       
      # if a record is a gene  
      if 'gene_id' in attributes:
        
        gene_id = _select_id(attributes, 'gene_id')
        biotype = attributes['biotype']
        description = attributes.get('description', '')

        gene = {'gene_id': gene_id, 'start': start, 'end': end, 
                'strand': strand, 'biotype': biotype, 
                'description': description}

        gene_dict.append(gene)

        continue
  
      # if the record is a transcript  
      elif 'transcript_id' in attributes:

        trns = _select_id(attributes, 'transcript_id')
        gn = _select_id(attributes, 'Parent')
        biotype = attributes['biotype']

        transcript = {'trans_id': trns, 'start': start, 'end': end, 
                      'strand': strand, 'biotype': biotype, 'gene': gn}

        trans_dict.append(transcript)

        continue

      # if the record is an exon 
      elif seqtype == 'exon':

        exon_id = _select_id(attributes, 'exon_id')
        trns = _select_id(attributes, 'Parent')
        exon_len = abs(end-start) + 1

        exon = {'exon_id': exon_id, 'start': start, 'end': end, 
                'exon_length': exon_len, 'strand': strand, 'transcript': trns}

        exon_dict.append(exon)

        continue

      else:
        continue

    return [gene_dict, trans_dict, exon_dict]

  except EOFError:

    err = 'EOFError: Compressed file ended before the end-of-stream marker was reached'
    print('!!! ERROR')
    print('An error happened while parsing the GFF file:')
    print(err)

    with open(config.ERRORLOG_DIR /'ErrorLogGffParsing.txt','a') as errorlog:
      errorlog.write('# ERROR in \n')
      errorlog.write(str(gff_path))
      errorlog.write('\n' + err + '\n')
    errorlog.close()

    return 'BAD-PARSING'